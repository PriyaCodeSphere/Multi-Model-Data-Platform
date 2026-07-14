"""LLM orchestrator that answers one customer question by consulting all
five paradigm views. Uses Azure OpenAI function-calling: the model decides
which of the five paradigm tools to invoke, we execute them against the
local pandas / graph / TF-IDF data, feed results back, and let the model
synthesise a final answer that cites which paradigm contributed what.

Credentials are loaded in this order:
1. st.secrets (Streamlit Community Cloud)
2. Environment variables (populated by python-dotenv locally)

The .env file itself is gitignored and must never be committed.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
from dotenv import find_dotenv, load_dotenv

try:
    import streamlit as st
except ImportError:  # allows unit-test import outside a Streamlit context
    st = None  # type: ignore

# Load .env once at import time so downstream `os.getenv` calls see it.
load_dotenv(find_dotenv(usecwd=True), override=False)


def _secret(name: str, default: str | None = None) -> str | None:
    """Read a secret from st.secrets first, falling back to environment."""
    if st is not None:
        try:
            if name in st.secrets:  # type: ignore[operator]
                return str(st.secrets[name])
        except Exception:
            pass
    return os.getenv(name, default)


@dataclass
class OrchestratorConfig:
    endpoint: str | None = field(default_factory=lambda: _secret("AZURE_OPENAI_ENDPOINT"))
    api_key: str | None = field(default_factory=lambda: _secret("AZURE_OPENAI_API_KEY"))
    deployment: str | None = field(default_factory=lambda: _secret("AZURE_OPENAI_CHAT_DEPLOYMENT"))
    api_version: str = field(
        default_factory=lambda: _secret("AZURE_OPENAI_API_VERSION", "2024-10-21") or "2024-10-21"
    )

    def is_ready(self) -> bool:
        return bool(self.endpoint and self.api_key and self.deployment)

    def missing(self) -> list[str]:
        missing = []
        if not self.endpoint:
            missing.append("AZURE_OPENAI_ENDPOINT")
        if not self.api_key:
            missing.append("AZURE_OPENAI_API_KEY")
        if not self.deployment:
            missing.append("AZURE_OPENAI_CHAT_DEPLOYMENT")
        return missing


# ---------------------------------------------------------------------------
# Tool definitions — one per paradigm. The `run` function must return a
# JSON-serialisable dict so we can echo it back to the LLM as tool output.
# ---------------------------------------------------------------------------


def _tool_query_orders(orders_df: pd.DataFrame, *, status: str | None = None,
                       region: str | None = None, quarter: str | None = None,
                       product_id: str | None = None, order_id: str | None = None,
                       limit: int = 10) -> dict:
    """Relational-style filter over the sales-order header table."""
    df = orders_df
    if order_id:
        df = df[df["order_id"] == order_id]
    if status:
        df = df[df["status"].str.lower() == status.lower()]
    if region:
        df = df[df["region"].str.lower() == region.lower()]
    if quarter:
        df = df[df["forecast_quarter"].str.lower() == quarter.lower()]
    if product_id:
        df = df[df["product_id"].str.lower() == product_id.lower()]

    return {
        "paradigm": "Relational (3NF)",
        "matching_orders": int(len(df)),
        "total_revenue": float(df["amount"].sum()),
        "sample": df[[
            "order_id", "customer_id", "product_id", "status",
            "region", "amount", "forecast_quarter"
        ]].head(limit).to_dict(orient="records"),
    }


def _tool_analyze_backlog(orders_df: pd.DataFrame, *, dimension: str = "region",
                          status: str | None = "Delayed") -> dict:
    """Star-schema-style aggregation."""
    df = orders_df
    if status:
        df = df[df["status"].str.lower() == status.lower()]

    if dimension not in {"region", "forecast_quarter", "product_id", "product_family", "status"}:
        dimension = "region"

    agg = (
        df.groupby(dimension)["amount"]
          .agg(order_count="count", revenue="sum")
          .sort_values("revenue", ascending=False)
          .reset_index()
    )
    return {
        "paradigm": "Dimensional (Star Schema)",
        "dimension": dimension,
        "filtered_by_status": status,
        "rows": [
            {dimension: row[dimension], "order_count": int(row["order_count"]),
             "revenue": float(row["revenue"])}
            for _, row in agg.iterrows()
        ],
    }


def _tool_get_order_json(orders_df: pd.DataFrame, *, order_id: str) -> dict:
    """Return the semi-structured JSON representation for one order."""
    matches = orders_df[orders_df["order_id"] == order_id]
    if matches.empty:
        return {"paradigm": "Semi-Structured (JSON)", "error": f"No order {order_id}"}
    row = matches.iloc[0]
    is_delayed = row["status"] == "Delayed"
    return {
        "paradigm": "Semi-Structured (JSON)",
        "order_id": row["order_id"],
        "customer_id": row["customer_id"],
        "product_id": row["product_id"],
        "product_name": row["product_name"],
        "quantity": int(row["quantity"]),
        "unit_price": float(row["unit_price"]),
        "amount": float(row["amount"]),
        "status": row["status"],
        "order_date": str(row["order_date"]),
        "forecast_quarter": row["forecast_quarter"],
        "region": row["region"],
        "shipping": {
            "priority": "high" if is_delayed else "standard",
            "expedited": is_delayed,
        },
    }


def _tool_supplier_impact(graph, orders_df: pd.DataFrame, *, supplier_id: str) -> dict:
    """Graph traversal from supplier to downstream orders."""
    analytics, impacted = graph.get_impact_analytics(supplier_id)
    return {
        "paradigm": "Graph",
        "supplier_id": supplier_id,
        "impacted_order_count": int(analytics["total_impacted_orders"]),
        "impacted_revenue": float(analytics["total_impacted_amount"]),
        "delayed_orders": int(analytics["delayed_orders"]),
        "impacted_regions": analytics["impacted_regions"],
        "sample_orders": impacted[["order_id", "customer_id", "status", "amount"]]
        .head(5).to_dict(orient="records") if len(impacted) else [],
    }


def _tool_search_knowledge_base(vector_engine, *, query: str, top_k: int = 3) -> dict:
    """TF-IDF retrieval over the knowledge documents."""
    results = vector_engine.search(query, top_k=top_k, similarity_threshold=0.05)
    return {
        "paradigm": "Vector / AI Knowledge",
        "query": query,
        "results": [
            {
                "source": r["metadata"]["doc_type"],
                "relevance": round(float(r["similarity_score"]), 3),
                "excerpt": r["excerpt"],
            }
            for r in results
        ],
    }


# ---------------------------------------------------------------------------
# Tool schemas advertised to the LLM
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "query_orders",
            "description": (
                "Relational lookup on the sales-order header table. Use for "
                "specific record lookups and simple filters (by status, region, "
                "quarter, product, or order_id). Returns matching row count, "
                "total revenue, and a sample."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "e.g. 'Delayed', 'Confirmed'"},
                    "region": {"type": "string", "description": "e.g. 'Europe', 'Asia Pacific'"},
                    "quarter": {"type": "string", "description": "e.g. 'Q3-2026'"},
                    "product_id": {"type": "string"},
                    "order_id": {"type": "string"},
                    "limit": {"type": "integer", "default": 10},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_backlog",
            "description": (
                "Dimensional aggregation (COUNT + SUM revenue) grouped by a "
                "dimension. Use for KPI-style questions ('by region', 'by "
                "product family', 'by quarter')."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "dimension": {
                        "type": "string",
                        "enum": ["region", "forecast_quarter", "product_id",
                                 "product_family", "status"],
                    },
                    "status": {"type": "string",
                               "description": "Optional status filter, default 'Delayed'."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_order_json",
            "description": (
                "Return the full semi-structured JSON representation of one "
                "order, including nested shipping and configuration attributes."
            ),
            "parameters": {
                "type": "object",
                "properties": {"order_id": {"type": "string"}},
                "required": ["order_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "supplier_impact",
            "description": (
                "Graph traversal from a supplier to all downstream orders it "
                "supplies via its components and products. Use for supply-chain "
                "risk / ripple-effect questions."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "supplier_id": {"type": "string",
                                     "description": "e.g. 'Supplier-S005'"},
                },
                "required": ["supplier_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_knowledge_base",
            "description": (
                "TF-IDF retrieval over supplier bulletins, engineering notes, "
                "quality alerts, and the service manual. Use for 'why is X "
                "happening' questions and root-cause explanations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "top_k": {"type": "integer", "default": 3},
                },
                "required": ["query"],
            },
        },
    },
]


SYSTEM_PROMPT = """You are the Prism multi-model orchestrator. You answer
customer questions about sales orders by consulting five different data
paradigms — each best at a different kind of question — and synthesising
a single grounded answer.

The five tools available to you:
  • query_orders          — relational lookups & simple filters
  • analyze_backlog       — star-schema aggregates by dimension
  • get_order_json        — semi-structured document for one order
  • supplier_impact       — graph traversal for supply-chain ripple
  • search_knowledge_base — vector retrieval for the 'why' behind delays

Rules:
1. For any non-trivial question, call at least two tools so the answer is
   grounded in multiple paradigms.
2. Prefer tool output over guessing. Never invent numbers.
3. When you present the final answer, briefly cite which paradigm(s)
   contributed each fact (e.g. 'per the relational count', 'via the
   graph traversal').
4. Keep answers concise and business-relevant. Do not repeat entire
   dataframes back to the user — summarise.
"""


@dataclass
class ToolCall:
    name: str
    arguments: dict
    result: dict


@dataclass
class OrchestratorResponse:
    answer: str
    tool_calls: list[ToolCall]
    error: str | None = None


class PrismOrchestrator:
    """Wraps Azure OpenAI + the five paradigm tools."""

    def __init__(self, orders_df: pd.DataFrame, graph, vector_engine,
                 config: OrchestratorConfig | None = None):
        self.orders_df = orders_df
        self.graph = graph
        self.vector_engine = vector_engine
        self.config = config or OrchestratorConfig()
        self._client = None

    def _ensure_client(self):
        if self._client is not None:
            return self._client
        if not self.config.is_ready():
            missing = ", ".join(self.config.missing())
            raise RuntimeError(f"Azure OpenAI not configured. Missing: {missing}")
        from openai import AzureOpenAI

        self._client = AzureOpenAI(
            api_key=self.config.api_key,
            api_version=self.config.api_version,
            azure_endpoint=self.config.endpoint,
        )
        return self._client

    def _dispatch(self, name: str, args: dict) -> dict:
        if name == "query_orders":
            return _tool_query_orders(self.orders_df, **args)
        if name == "analyze_backlog":
            return _tool_analyze_backlog(self.orders_df, **args)
        if name == "get_order_json":
            return _tool_get_order_json(self.orders_df, **args)
        if name == "supplier_impact":
            return _tool_supplier_impact(self.graph, self.orders_df, **args)
        if name == "search_knowledge_base":
            return _tool_search_knowledge_base(self.vector_engine, **args)
        return {"error": f"unknown tool: {name}"}

    def ask(self, question: str, *, max_tool_rounds: int = 4) -> OrchestratorResponse:
        try:
            client = self._ensure_client()
        except RuntimeError as e:
            return OrchestratorResponse(answer="", tool_calls=[], error=str(e))

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
        tool_calls_recorded: list[ToolCall] = []

        for _ in range(max_tool_rounds):
            resp = client.chat.completions.create(
                model=self.config.deployment,
                messages=messages,
                tools=TOOL_SCHEMAS,
                tool_choice="auto",
                temperature=0.2,
            )
            msg = resp.choices[0].message

            if not msg.tool_calls:
                return OrchestratorResponse(
                    answer=msg.content or "",
                    tool_calls=tool_calls_recorded,
                )

            messages.append({
                "role": "assistant",
                "content": msg.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments},
                    }
                    for tc in msg.tool_calls
                ],
            })

            for tc in msg.tool_calls:
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                result = self._dispatch(tc.function.name, args)
                tool_calls_recorded.append(ToolCall(
                    name=tc.function.name, arguments=args, result=result,
                ))
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": json.dumps(result, default=str),
                })

        return OrchestratorResponse(
            answer=(
                "I explored multiple paradigms but did not reach a final synthesised "
                "answer within the tool-call budget. Please refine the question."
            ),
            tool_calls=tool_calls_recorded,
        )
