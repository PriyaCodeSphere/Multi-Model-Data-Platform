"""Multi-agent orchestration over the five paradigms.

Where utils/orchestrator.py runs ONE LLM that can call five tools,
this module runs SEVEN LLMs collaborating:

    1. Router          — decomposes the user question and picks specialists
    5x Specialists     — each an expert on one paradigm, with just that
                         paradigm's tool available
    1. Synthesiser     — combines specialist findings into a final answer

This is the 'agent per data domain' pattern enterprises reach for when
they want each paradigm to have a clear owner, its own prompt, and its
own boundaries. It costs more LLM calls per question (typically 3-5x)
but makes the collaboration visible, which is what makes it worth
showing in a demo.

The existing single-agent Ask tab is untouched; this is a parallel
implementation intended to sit in its own tab.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

from utils.orchestrator import (
    OrchestratorConfig,
    _tool_analyze_backlog,
    _tool_get_order_json,
    _tool_query_orders,
    _tool_search_knowledge_base,
    _tool_supplier_impact,
)


# ---------------------------------------------------------------------------
# Specialist profiles — each maps to exactly one paradigm tool.
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class SpecialistProfile:
    name: str            # display name, e.g. "Relational Analyst"
    role: str            # one-line description shown in the UI
    tool_name: str       # matches a tool schema in orchestrator.py
    tool_schema: dict    # OpenAI-format tool schema for this one tool
    system_prompt: str   # role-specific system prompt


SPECIALISTS: dict[str, SpecialistProfile] = {
    "relational": SpecialistProfile(
        name="Relational Analyst",
        role="Master-record lookups and exact filters on the sales-order table.",
        tool_name="query_orders",
        tool_schema={
            "type": "function",
            "function": {
                "name": "query_orders",
                "description": "Exact filter over the sales-order header table.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "status": {"type": "string"},
                        "region": {"type": "string"},
                        "quarter": {"type": "string"},
                        "product_id": {"type": "string"},
                        "order_id": {"type": "string"},
                        "limit": {"type": "integer", "default": 10},
                    },
                },
            },
        },
        system_prompt=(
            "You are the Relational Analyst. Your only tool is `query_orders`. "
            "If the sub-question names a specific order_id, ALWAYS pass it and "
            "report the returned sample[0].amount as that order's total sales "
            "value (= quantity x unit_price). For filter-based questions, use "
            "the appropriate status / region / quarter / product filters. Copy "
            "dollar figures verbatim from the tool response - never round or "
            "approximate. Return a two-sentence finding grounded in the tool "
            "result."
        ),
    ),
    "dimensional": SpecialistProfile(
        name="Dimensional Analyst",
        role="Star-schema aggregates: counts and revenue by dimension.",
        tool_name="analyze_backlog",
        tool_schema={
            "type": "function",
            "function": {
                "name": "analyze_backlog",
                "description": "Aggregate orders grouped by a dimension.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "dimension": {
                            "type": "string",
                            "enum": ["region", "forecast_quarter", "product_id",
                                     "product_family", "status"],
                        },
                        "status": {"type": "string"},
                    },
                },
            },
        },
        system_prompt=(
            "You are the Dimensional Analyst. Your only tool is `analyze_backlog`. "
            "Use it to break the sub-question down by region / quarter / product / "
            "family / status. Highlight the top contributor. Return a two-sentence "
            "finding with the specific numbers."
        ),
    ),
    "json": SpecialistProfile(
        name="Document Analyst",
        role="Full semi-structured JSON for a specific order.",
        tool_name="get_order_json",
        tool_schema={
            "type": "function",
            "function": {
                "name": "get_order_json",
                "description": "Fetch the full JSON payload for one order.",
                "parameters": {
                    "type": "object",
                    "properties": {"order_id": {"type": "string"}},
                    "required": ["order_id"],
                },
            },
        },
        system_prompt=(
            "You are the Document Analyst. Your only tool is `get_order_json`. "
            "Use it when the sub-question needs the messy per-order attributes "
            "(shipping priority, expedited flag, engine options). If no specific "
            "order id is given, say so — do not guess. Return a two-sentence "
            "finding grounded in the tool result."
        ),
    ),
    "graph": SpecialistProfile(
        name="Graph Analyst",
        role="Supply-chain traversal: supplier → component → product → order.",
        tool_name="supplier_impact",
        tool_schema={
            "type": "function",
            "function": {
                "name": "supplier_impact",
                "description": "Traverse the graph from a supplier to its downstream orders.",
                "parameters": {
                    "type": "object",
                    "properties": {"supplier_id": {"type": "string"}},
                    "required": ["supplier_id"],
                },
            },
        },
        system_prompt=(
            "You are the Graph Analyst. Your only tool is `supplier_impact`. "
            "Use it to expose ripple effects — how many downstream orders and "
            "how much revenue a supplier disruption would touch. Return a "
            "two-sentence finding grounded in the tool result."
        ),
    ),
    "vector": SpecialistProfile(
        name="Knowledge Analyst",
        role="Retrieval from supplier bulletins, engineering notes, quality alerts.",
        tool_name="search_knowledge_base",
        tool_schema={
            "type": "function",
            "function": {
                "name": "search_knowledge_base",
                "description": "TF-IDF retrieval over the knowledge documents.",
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
        system_prompt=(
            "You are the Knowledge Analyst. Your only tool is `search_knowledge_base`. "
            "Use it to explain WHY events are happening by pulling relevant supplier "
            "bulletins, engineering notes and quality alerts. Cite the document type "
            "and a short excerpt. Return a two-sentence finding grounded in the tool "
            "result."
        ),
    ),
}


ROUTER_SYSTEM_PROMPT = """You are the Router in a multi-agent squad. Given a
user's business question about sales orders, decompose it into sub-questions
and dispatch each to the right specialist.

Available specialists:
  • relational   — exact lookups and filtered counts / revenue
  • dimensional  — aggregates grouped by region / quarter / product / status
  • json         — messy per-order attributes (shipping, engine options)
  • graph        — supplier -> component -> product -> order ripple effects
  • vector       — root-cause explanations from bulletins and alerts

Return ONLY a JSON object of the form:
{
  "plan": [
    {"specialist": "<key>", "sub_question": "<focused question just for that specialist>"},
    ...
  ],
  "rationale": "<one sentence on why this decomposition>"
}

Rules:
1. Include at least one specialist. For most non-trivial questions include 2-4.
2. Never include the same specialist twice.
3. Sub-questions must be focused enough for that one specialist to answer
   using only its tool.
4. Prefer diversity of paradigms — if a question could be answered by one
   paradigm alone, still consider whether another paradigm adds a useful angle.
"""


SYNTHESISER_SYSTEM_PROMPT = """You are the Synthesiser in a multi-agent squad.
You receive the user's original question, the router's rationale, and each
specialist's finding. Combine them into ONE grounded answer.

Rules:
1. Never invent numbers. Every fact must trace to a specialist finding.
2. Cite which specialist contributed each fact, in plain English (e.g.
   'per the Relational Analyst', 'the Graph Analyst found...').
3. If specialists disagree or one had no data, flag it explicitly.
4. End with a one-line takeaway. Keep the total answer under ~150 words.
"""


# ---------------------------------------------------------------------------
# Data classes for the response payload
# ---------------------------------------------------------------------------

@dataclass
class SpecialistOutcome:
    specialist_key: str
    specialist_name: str
    sub_question: str
    tool_name: str
    tool_arguments: dict = field(default_factory=dict)
    tool_result: dict = field(default_factory=dict)
    finding: str = ""


@dataclass
class AgentSquadResponse:
    plan: list[dict]                 # [{specialist, sub_question}, ...]
    plan_rationale: str
    outcomes: list[SpecialistOutcome]
    final_answer: str
    error: str | None = None


# ---------------------------------------------------------------------------
# Multi-agent squad
# ---------------------------------------------------------------------------

class PrismAgentSquad:
    """Router + 5 specialists + synthesiser sharing one Azure OpenAI deployment."""

    def __init__(self, orders_df, graph, vector_engine,
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

    def _dispatch_tool(self, name: str, args: dict) -> dict:
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

    # ------------- Step 1: Router plans -----------------------------------
    def _plan(self, question: str) -> tuple[list[dict], str]:
        client = self._ensure_client()
        resp = client.chat.completions.create(
            model=self.config.deployment,
            messages=[
                {"role": "system", "content": ROUTER_SYSTEM_PROMPT},
                {"role": "user", "content": question},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw = resp.choices[0].message.content or "{}"
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            data = {}
        plan_items = [
            item for item in data.get("plan", [])
            if isinstance(item, dict)
            and item.get("specialist") in SPECIALISTS
            and item.get("sub_question")
        ]
        # Deduplicate specialists, preserve order
        seen = set()
        deduped = []
        for item in plan_items:
            if item["specialist"] in seen:
                continue
            seen.add(item["specialist"])
            deduped.append(item)
        return deduped, str(data.get("rationale", ""))

    # ------------- Step 2: Each specialist works --------------------------
    def _run_specialist(self, key: str, sub_question: str) -> SpecialistOutcome:
        client = self._ensure_client()
        prof = SPECIALISTS[key]
        outcome = SpecialistOutcome(
            specialist_key=key,
            specialist_name=prof.name,
            sub_question=sub_question,
            tool_name=prof.tool_name,
        )

        first = client.chat.completions.create(
            model=self.config.deployment,
            messages=[
                {"role": "system", "content": prof.system_prompt},
                {"role": "user", "content": sub_question},
            ],
            tools=[prof.tool_schema],
            tool_choice="auto",
            temperature=0.1,
        )
        msg = first.choices[0].message

        if msg.tool_calls:
            tc = msg.tool_calls[0]
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {}
            outcome.tool_arguments = args
            outcome.tool_result = self._dispatch_tool(tc.function.name, args)

            follow = client.chat.completions.create(
                model=self.config.deployment,
                messages=[
                    {"role": "system", "content": prof.system_prompt},
                    {"role": "user", "content": sub_question},
                    {
                        "role": "assistant",
                        "content": msg.content,
                        "tool_calls": [{
                            "id": tc.id,
                            "type": "function",
                            "function": {"name": tc.function.name,
                                         "arguments": tc.function.arguments},
                        }],
                    },
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(outcome.tool_result, default=str),
                    },
                ],
                temperature=0.1,
            )
            outcome.finding = follow.choices[0].message.content or ""
        else:
            outcome.finding = msg.content or "(no tool call made)"

        return outcome

    # ------------- Step 3: Synthesiser combines ---------------------------
    def _synthesise(self, question: str, rationale: str,
                    outcomes: list[SpecialistOutcome]) -> str:
        client = self._ensure_client()
        specialist_block = "\n\n".join(
            f"### {o.specialist_name}\n"
            f"Sub-question: {o.sub_question}\n"
            f"Finding: {o.finding}"
            for o in outcomes
        )
        resp = client.chat.completions.create(
            model=self.config.deployment,
            messages=[
                {"role": "system", "content": SYNTHESISER_SYSTEM_PROMPT},
                {"role": "user", "content": (
                    f"Original question: {question}\n\n"
                    f"Router rationale: {rationale}\n\n"
                    f"Specialist findings:\n\n{specialist_block}"
                )},
            ],
            temperature=0.2,
        )
        return resp.choices[0].message.content or ""

    # ------------- Public entry point ------------------------------------
    def ask(self, question: str) -> AgentSquadResponse:
        try:
            plan, rationale = self._plan(question)
            if not plan:
                return AgentSquadResponse(
                    plan=[], plan_rationale=rationale, outcomes=[],
                    final_answer=(
                        "The Router did not produce a usable plan for this "
                        "question. Try rephrasing with more specific business terms."
                    ),
                )
            outcomes = [
                self._run_specialist(item["specialist"], item["sub_question"])
                for item in plan
            ]
            final = self._synthesise(question, rationale, outcomes)
            return AgentSquadResponse(
                plan=plan, plan_rationale=rationale,
                outcomes=outcomes, final_answer=final,
            )
        except Exception as exc:  # noqa: BLE001 — surface any failure to the UI
            return AgentSquadResponse(
                plan=[], plan_rationale="", outcomes=[],
                final_answer="", error=str(exc),
            )
