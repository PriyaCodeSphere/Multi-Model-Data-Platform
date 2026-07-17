"""
Prism Multi-Model Framework Demonstrator
Production-Quality Streamlit Application

Demonstrates how a single canonical Sales Order object can be projected
into five different data paradigms: Relational, Dimensional, Semi-Structured,
Graph, and Vector/AI Knowledge Retrieval.
"""

import hashlib
import json
import os
import sys
from datetime import datetime


def _boot(msg: str) -> None:
    print(f"[Prism-BOOT] {msg}", flush=True)


_boot("importing numpy/pandas/plotly/streamlit")
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

_boot("importing project utils")
from utils.data_generator import load_or_generate_data
from utils.routing import get_all_questions, get_model_recommendation
from utils.graph_builder import SupplierImpactGraph
from utils.embeddings import VectorSearchEngine
from utils.orchestrator import PrismOrchestrator, OrchestratorConfig
from utils.agent_squad import PrismAgentSquad, SPECIALISTS

_boot(
    f"env: python={sys.version.split()[0]}, "
    f"streamlit={st.__version__}, pandas={pd.__version__}, numpy={np.__version__}"
)


def _order_rng(order_id: str) -> np.random.Generator:
    """Deterministic per-order RNG so rendered attributes are stable across reruns."""
    seed = int(hashlib.sha256(str(order_id).encode()).hexdigest()[:8], 16)
    return np.random.default_rng(seed)


def _engine_options_for(order_id: str) -> dict:
    rng = _order_rng(order_id)
    return {
        "turbocharger": "advanced" if rng.random() > 0.5 else "standard",
        "cooling": "heavy-duty" if rng.random() > 0.5 else "standard",
        "emission_standard": "Euro 6" if rng.random() > 0.5 else "Stage 5",
    }


def _line_items_for(order_id: str, max_lines: int = 4) -> pd.DataFrame:
    rng = _order_rng(order_id)
    num_lines = int(rng.integers(1, max_lines + 1))
    return pd.DataFrame([
        {
            "line_number": i + 1,
            "component_id": f"COMP-{int(rng.integers(1000, 9999))}",
            "qty": int(rng.integers(1, 20)),
            "unit_price": round(float(rng.uniform(1000, 50000)), 2),
        }
        for i in range(num_lines)
    ])

def _build_impact_diagram(graph, order_id: str, supplier_id: str, orders_df: pd.DataFrame) -> go.Figure:
    """Node-link figure: supplier -> components -> product -> orders (selected highlighted)."""
    order_matches = orders_df[orders_df["order_id"] == order_id]
    if order_matches.empty:
        return go.Figure()
    order_row = order_matches.iloc[0]
    product_id = order_row["product_id"]
    product_name = order_row["product_name"]

    edges_df = graph.edges_df
    supplier_comps = set(graph.supplier_components.get(supplier_id, []))
    product_comps = set(edges_df[
        (edges_df["target"] == product_id)
        & (edges_df["relationship"] == "belongs_to")
    ]["source"])
    shared = sorted(supplier_comps & product_comps)[:5]
    if not shared:
        shared = sorted(supplier_comps)[:5]

    peer_orders = orders_df[
        (orders_df["product_id"] == product_id) & (orders_df["order_id"] != order_id)
    ]["order_id"].head(4).tolist()
    orders_shown = [order_id] + peer_orders

    def _stack(n: int) -> list[float]:
        return [i - (n - 1) / 2 for i in range(n)]

    comp_ys = _stack(len(shared))
    ord_ys = _stack(len(orders_shown))

    node_x, node_y, node_labels, node_colors, node_sizes, node_hover = [], [], [], [], [], []

    def add_node(x, y, label, color, size, hover):
        node_x.append(x); node_y.append(y)
        node_labels.append(label); node_colors.append(color)
        node_sizes.append(size); node_hover.append(hover)

    add_node(0, 0, supplier_id, "#FFCC00", 30, f"Supplier: {supplier_id}")
    for c, y in zip(shared, comp_ys):
        add_node(1, y, c, "#9E9E9E", 20, f"Component: {c}")
    add_node(2, 0, product_id, "#111111", 30, f"Product: {product_id} ({product_name})")
    for oid, y in zip(orders_shown, ord_ys):
        is_selected = oid == order_id
        add_node(3, y, oid, "#DC0000" if is_selected else "#F5B7B1",
                 30 if is_selected else 20,
                 f"Order: {oid}{' (selected)' if is_selected else ''}")

    edge_x, edge_y = [], []
    for cy in comp_ys:
        edge_x.extend([0, 1, None]); edge_y.extend([0, cy, None])
        edge_x.extend([1, 2, None]); edge_y.extend([cy, 0, None])
    for oy in ord_ys:
        edge_x.extend([2, 3, None]); edge_y.extend([0, oy, None])

    fig = go.Figure(
        data=[
            go.Scatter(x=edge_x, y=edge_y, mode="lines",
                       line=dict(color="#D0D0D0", width=1.2), hoverinfo="none"),
            go.Scatter(x=node_x, y=node_y, mode="markers+text",
                       marker=dict(color=node_colors, size=node_sizes,
                                   line=dict(color="white", width=1.5)),
                       text=node_labels, textposition="bottom center",
                       textfont=dict(size=10, color="#111111"),
                       hovertext=node_hover, hoverinfo="text"),
        ]
    )
    for x, label in enumerate(["Supplier", "Components", "Product", "Orders"]):
        fig.add_annotation(x=x, y=1.05, xref="x", yref="paper",
                           text=f"<b>{label}</b>", showarrow=False,
                           font=dict(size=11, color="#6b6b6b"))
    fig.update_layout(
        showlegend=False, plot_bgcolor="white",
        margin=dict(l=10, r=10, t=40, b=20), height=380,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 3.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
    )
    return fig


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Prism Multi-Model Framework Demonstrator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS — minimal, professional enterprise-inspired theme
st.markdown("""
<style>
    /* Tighten Streamlit's default gutters and top padding */
    .block-container {
        padding-top: 1.25rem !important;
        padding-bottom: 1rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 100% !important;
    }
    /* Trim vertical whitespace between blocks */
    div[data-testid="stVerticalBlock"] > div {
        gap: 0.5rem;
    }
    /* Hide the "Deploy" ribbon / Streamlit chrome so the header sits flush */
    header[data-testid="stHeader"] {
        height: 0;
        background: transparent;
    }
    #MainMenu, footer { visibility: hidden; }

    .app-title {
        color: #111111;
        font-weight: 600;
        font-size: 1.9rem;
        margin: 0 0 0.15rem 0;
        letter-spacing: -0.01em;
    }
    .app-subtitle {
        color: #6b6b6b;
        font-size: 0.95rem;
        margin: 0 0 1rem 0;
    }
    .order-card {
        background: #FAFAFA;
        border: 1px solid #E5E5E5;
        border-left: 3px solid #FFCC00;
        border-radius: 6px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.5rem;
    }
    .order-card .field-label {
        color: #6b6b6b;
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.15rem;
    }
    .order-card .field-value {
        color: #111111;
        font-size: 0.95rem;
        font-weight: 500;
    }
    .status-pill {
        display: inline-block;
        padding: 0.15rem 0.6rem;
        border-radius: 999px;
        font-size: 0.8rem;
        font-weight: 500;
    }
    .status-danger  { background: #FDECEA; color: #B71C1C; }
    .status-ok      { background: #E8F5E9; color: #1B5E20; }
    .status-neutral { background: #ECEFF1; color: #37474F; }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

@st.cache_resource
def load_data():
    """Load synthetic data"""
    return load_or_generate_data("data")

@st.cache_resource
def initialize_vector_search():
    """Initialize vector search engine"""
    engine = VectorSearchEngine()
    engine.load_documents_from_directory("data/documents")
    return engine

@st.cache_resource
def build_graph(_data):
    """Build knowledge graph.

    The leading underscore on _data tells Streamlit to skip hashing this
    argument. Hashing a dict of pandas DataFrames segfaults on Python 3.14
    with pandas 3.0 / numpy 2.5. The cache key falls back to the function's
    identity, which is exactly what we want for this one-shot build.
    """
    return SupplierImpactGraph(
        _data["graph_edges"],
        _data["products"],
        _data["suppliers"],
        _data["orders"],
    )

_boot("calling load_data()")
data = load_data()
_boot(f"load_data ok: {len(data['orders'])} orders")
orders_df = data["orders"]
suppliers_df = data["suppliers"]
products_df = data["products"]
graph_edges_df = data["graph_edges"]

_boot("calling initialize_vector_search()")
vector_engine = initialize_vector_search()
_boot(f"vector_engine ok: {len(vector_engine.documents)} docs indexed")

_boot("calling build_graph()")
graph = build_graph(data)
_boot(f"graph ok: {len(graph.supplier_components)} suppliers mapped")

_boot("all init complete, rendering UI")

# Initialize session state
if "selected_order" not in st.session_state:
    st.session_state.selected_order = orders_df.iloc[0]["order_id"]

if "selected_question" not in st.session_state:
    st.session_state.selected_question = "Show Sales Order Details"

# ---- Header -----------------------------------------------------------------
_boot("UI: header")

st.markdown(
    '<div class="app-title">Prism Multi-Model Framework Demonstrator</div>'
    '<div class="app-subtitle">One canonical sales order, projected into five optimised data paradigms — see which model each business team should use.</div>',
    unsafe_allow_html=True,
)

with st.expander("About this demo · how to use it"):
    st.markdown(
        """
**What this shows**

Enterprise data teams keep asking the same question: *do we really need more than one data model?*
This demo answers it with a live illustration. Pick any sales order and watch five different data
paradigms represent that same transaction — each optimised for a different consumer.

| Paradigm | Best for | Typical consumer |
| --- | --- | --- |
| **Relational (3NF)** | Single-record lookups, transactional integrity | OMS teams, operational APIs |
| **Dimensional (Star Schema)** | Aggregate KPIs, revenue by region/quarter | COO, Finance, S&OP |
| **Semi-Structured (JSON)** | Variable attributes, API payloads, ML features | Data science, external integrations |
| **Graph** | Relationship traversal, supplier impact | Supply chain, risk management |
| **Vector / AI** | Contextual knowledge retrieval, root-cause explanations | AI assistants, knowledge workers |

**How to use it**

1. Pick a **business question** on the left. The callout below tells you which tab answers it best.
2. Pick a **sales order** on the right. Every tab below re-grounds itself around that specific order.
3. Open any tab to see how that data model represents your chosen transaction —
   including the SQL / Cypher / API call a real team would run.
4. On the **Graph** tab, the supplier picker defaults to the supplier most involved with your order.
   Switch to a different supplier to explore *"what if this vendor slips?"* ripple effects.
5. On the **Vector / AI** tab, ask a natural-language question about the order — the knowledge base
   returns the supporting documents and a summarised root cause.
6. On the **Compare** tab, see one question answered through all five paradigms at once —
   with the actual queries and results side-by-side.
7. On the **Ask** tab, type any question about the orders. An LLM (Azure OpenAI) decides which of
   the five paradigms to consult, runs the queries, and synthesises an answer that cites which
   paradigm contributed each fact.
8. On the **Agents** tab, see the same problem solved with the *agent-per-domain* pattern:
   a Router LLM plans, five specialist LLMs each handle their own paradigm, and a Synthesiser
   LLM combines the findings — every step visible in collapsible panels.

*All data is synthetic. No real the customer, supplier, or transaction is represented.*
        """
    )

# ---- Controls: business question + sales order ------------------------------
_boot("UI: controls row")

questions = get_all_questions()
sel_col, ord_col = st.columns(2)

with sel_col:
    selected_question = st.selectbox(
        "Business question",
        questions,
        index=questions.index(st.session_state.selected_question),
        key="question_select",
    )
    st.session_state.selected_question = selected_question

with ord_col:
    selected_order_id = st.selectbox(
        "Sales order",
        orders_df["order_id"].unique(),
        index=list(orders_df["order_id"]).index(st.session_state.selected_order),
        key="order_select",
    )
    st.session_state.selected_order = selected_order_id

selected_order_data = orders_df[orders_df["order_id"] == selected_order_id].iloc[0]
question_info = get_model_recommendation(selected_question)

# ---- Recommendation callout -------------------------------------------------
_boot("UI: recommendation callout")

if question_info:
    st.info(
        f"**Recommended view:** {question_info['model']} tab · "
        f"{question_info['reason']} · *Consumer:* {question_info['persona']}"
    )

# ---- Selected-order summary card -------------------------------------------
_boot("UI: order summary")

AT_RISK_STATUSES = ("On Hold", "Back Ordered", "Cancelled")
DONE_STATUSES = ("Shipped", "Delivered", "Invoiced")

_status = str(selected_order_data["status"])
_status_class = (
    "status-danger" if _status in AT_RISK_STATUSES
    else "status-ok" if _status in DONE_STATUSES
    else "status-neutral"
)

_fields = [
    ("Order ID", selected_order_data["order_id"]),
    ("Customer", selected_order_data["customer_id"]),
    ("Product", selected_order_data["product_name"]),
    ("Region", selected_order_data["region"]),
    ("Quantity", f"{int(selected_order_data['quantity'])} units"),
    ("Amount", f"${selected_order_data['amount']:,.0f}"),
    ("Forecast Quarter", selected_order_data["forecast_quarter"]),
    ("Status", f'<span class="status-pill {_status_class}">{_status}</span>'),
]

_field_html = "".join(
    f'<div><div class="field-label">{label}</div>'
    f'<div class="field-value">{value}</div></div>'
    for label, value in _fields
)

st.markdown(
    f'<div class="order-card">'
    f'<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:1rem 1.5rem;">'
    f'{_field_html}'
    f'</div></div>',
    unsafe_allow_html=True,
)

st.divider()

# ============================================================================
_boot("UI: tab bar")
# TAB SECTION: FIVE DATA PARADIGMS
# ============================================================================

tabs = st.tabs([
    "1️⃣ Relational",
    "2️⃣ Dimensional",
    "3️⃣ JSON",
    "4️⃣ Graph",
    "5️⃣ Vector/AI",
    "🔀 Compare",
    "💬 Ask",
    "🤖 Agents",
])

# ============================================================================
_boot("UI: tab1 relational")
# TAB 1: RELATIONAL MODEL
# ============================================================================

with tabs[0]:
    st.markdown("## Relational Projection (3NF)")
    
    col1, col2 = st.columns(2)
    
    st.caption(f"Showing the relational projection for **{selected_order_id}**")

    with col1:
        st.markdown("### SALES_ORDER_HDR")

        header_data = orders_df[orders_df["order_id"] == selected_order_id][[
            "order_id", "customer_id", "product_id", "order_date", "status", "amount"
        ]]
        st.dataframe(header_data, width='stretch', hide_index=True)

        st.markdown("#### Query that produced this row")
        st.code(
            f"SELECT order_id, customer_id, product_id, status, amount\n"
            f"FROM SALES_ORDER_HDR\n"
            f"WHERE order_id = '{selected_order_id}';",
            language="sql",
        )

    with col2:
        st.markdown("### SALES_ORDER_LINE")

        lines_df = _line_items_for(selected_order_id)
        st.dataframe(lines_df, width='stretch', hide_index=True)

        st.markdown("#### Query that produced these rows")
        st.code(
            f"SELECT line_number, component_id, qty, unit_price\n"
            f"FROM SALES_ORDER_LINE\n"
            f"WHERE order_id = '{selected_order_id}'\n"
            f"ORDER BY line_number;",
            language="sql",
        )
    
    st.divider()
    
    st.markdown("### Business Purpose")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("🎯 **Master Record Lookup**\nOperational APIs and OMS systems query individual orders")
    
    with col2:
        st.info("🔒 **Referential Integrity**\nNormalized structure ensures data consistency")
    
    with col3:
        st.info("👥 **Consumer Personas**\nOMS Team, EOMP, Operational APIs")

# ============================================================================
_boot("UI: tab2 dimensional")
# TAB 2: DIMENSIONAL MODEL (STAR SCHEMA)
# ============================================================================

with tabs[1]:
    st.markdown("## Dimensional Projection (Star Schema)")
    
    col1, col2 = st.columns(2)
    
    order_region = selected_order_data["region"]
    order_quarter = selected_order_data["forecast_quarter"]

    st.caption(
        f"Showing the dimensional context for **{selected_order_id}** — "
        f"region **{order_region}**, quarter **{order_quarter}**"
    )

    with col1:
        st.markdown("### FACT_SALES_ORDER — this order")

        fact_row = orders_df[orders_df["order_id"] == selected_order_id][[
            "order_id", "customer_id", "product_id", "amount", "status", "forecast_quarter", "region"
        ]]
        st.dataframe(fact_row, width='stretch', hide_index=True)

        st.markdown("### Dimensions this fact joins to")

        st.markdown("#### DIM_CUSTOMER")
        dim_customer = pd.DataFrame([{
            "customer_id": selected_order_data["customer_id"],
            "region": order_region,
        }])
        st.dataframe(dim_customer, width='stretch', hide_index=True)

        st.markdown("#### DIM_PRODUCT")
        product_row = products_df[products_df["id"] == selected_order_data["product_id"]]
        if not product_row.empty:
            p = product_row.iloc[0]
            dim_product = pd.DataFrame([{
                "product_id": p["id"],
                "product_name": p["name"],
                "product_family": p["family"],
                "unit_cost": f"${float(p['unit_cost']):,.0f}",
                "lead_time_days": int(p["lead_time_days"]),
            }])
        else:
            dim_product = pd.DataFrame([{
                "product_id": selected_order_data["product_id"],
                "product_name": selected_order_data["product_name"],
                "product_family": selected_order_data.get("product_family", ""),
            }])
        st.dataframe(dim_product, width='stretch', hide_index=True)

        st.markdown("#### DIM_DATE")
        dim_date = pd.DataFrame([{
            "date_key": str(selected_order_data["order_date"])[:10],
            "quarter": order_quarter,
        }])
        st.dataframe(dim_date, width='stretch', hide_index=True)

    with col2:
        st.markdown("### This order in its aggregate context")

        # Highlight the selected order's region in the revenue-by-region chart
        revenue_by_region = orders_df.groupby("region")["amount"].sum().reset_index()
        revenue_by_region.columns = ["Region", "Revenue"]
        revenue_by_region["highlight"] = revenue_by_region["Region"].eq(order_region).map(
            {True: "This order's region", False: "Other regions"}
        )

        fig1 = px.bar(
            revenue_by_region,
            x="Region",
            y="Revenue",
            color="highlight",
            title="Total Revenue by Region",
            color_discrete_map={"This order's region": "#FFCC00", "Other regions": "#CCCCCC"},
        )
        fig1.update_layout(plot_bgcolor="rgba(0,0,0,0.05)", paper_bgcolor="white", font=dict(color="#000000"))
        st.plotly_chart(fig1, width='stretch')

        # Quarter contribution: this order's amount vs its quarter's total
        quarter_total = orders_df[orders_df["forecast_quarter"] == order_quarter]["amount"].sum()
        this_amount = float(selected_order_data["amount"])
        share_pct = 100 * this_amount / quarter_total if quarter_total else 0
        st.metric(
            label=f"This order's contribution to {order_quarter}",
            value=f"${this_amount:,.0f}",
            delta=f"{share_pct:.2f}% of ${quarter_total:,.0f} quarter total",
            delta_color="off",
        )

    st.divider()

    st.markdown("#### Query that produced this view")
    st.code(
        f"SELECT d.quarter,\n"
        f"       c.region,\n"
        f"       p.product_family,\n"
        f"       COUNT(*) as order_count,\n"
        f"       SUM(f.amount) as total_revenue,\n"
        f"       AVG(f.amount) as avg_order_value\n"
        f"FROM FACT_SALES_ORDER f\n"
        f"JOIN DIM_DATE     d ON f.date_key     = d.date_key\n"
        f"JOIN DIM_CUSTOMER c ON f.customer_key = c.customer_key\n"
        f"JOIN DIM_PRODUCT  p ON f.product_key  = p.product_key\n"
        f"WHERE d.quarter = '{order_quarter}'\n"
        f"  AND c.region  = '{order_region}'\n"
        f"GROUP BY d.quarter, c.region, p.product_family;",
        language="sql",
    )
    
    st.divider()
    
    st.markdown("### Business Purpose")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success("📊 **Executive Analytics**\nPower BI and analytics dashboards")
    
    with col2:
        st.success("📈 **KPI Tracking**\nRevenue, bookings, forecast analysis")
    
    with col3:
        st.success("👥 **Consumer Personas**\nCOO, Finance, S&OP teams")

# ============================================================================
_boot("UI: tab3 json")
# TAB 3: JSON MODEL (SEMI-STRUCTURED)
# ============================================================================

with tabs[2]:
    st.markdown("## Semi-Structured Projection (JSON)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### JSON Order Payload")
        
        is_at_risk = selected_order_data["status"] in AT_RISK_STATUSES
        json_payload = {
            "order_id": selected_order_data["order_id"],
            "customer_id": selected_order_data["customer_id"],
            "product_id": selected_order_data["product_id"],
            "quantity": int(selected_order_data["quantity"]),
            "status": selected_order_data["status"],
            "promo_codes": ["SUMMER26", "BULK20"],
            "engine_options": _engine_options_for(selected_order_data["order_id"]),
            "transmission": {
                "type": "powershift",
                "gears": 16,
            },
            "shipping": {
                "method": "Air Freight" if is_at_risk else "Sea Freight",
                "priority": "high" if is_at_risk else "standard",
                "expedited": is_at_risk,
                "insurance": True,
            },
            "metadata": {
                "created_at": str(selected_order_data["order_date"]),
                "source_system": "OMS",
                "version": "2.1",
                "compliance_flags": ["export_control", "hazmat"],
            },
        }

        st.json(json_payload)
    
    with col2:
        st.markdown("### Schema Flexibility Benefits")
        
        st.info("""
        ✅ **Dynamic Schema Evolution**
        - Add new attributes without migration
        - Support variable product configurations
        - Enable rapid feature deployment
        
        ✅ **Nested Structures**
        - Complex relationships in single document
        - Engine options, shipping, metadata co-located
        - Reduces join complexity in analytics
        
        ✅ **API-First Design**
        - JSON native for REST/GraphQL services
        - Easier external system integration
        - Supports semi-structured data ingestion
        """)
        
        st.markdown("### Consumer Scenarios")
        
        st.markdown("#### Data Science & ML")
        st.code("""
import json
orders = load_json_documents('orders/')
for order in orders:
    features = extract_features(
        order['engine_options'],
        order['shipping'],
        order['metadata']
    )
        """, language="python")
        
        st.markdown("#### External API Integration")
        st.code("""
POST /api/v2/orders
Content-Type: application/json

{
  "order_id": "SO-1000456",
  "engine_options": {...},
  "shipping": {...}
}
        """, language="json")

# ============================================================================
_boot("UI: tab4 graph")
# TAB 4: GRAPH MODEL
# ============================================================================

with tabs[3]:
    st.markdown("## Relationship Projection (Graph Model)")
    
    st.markdown("### Supplier Impact Analysis")

    # Trace this order's supplier dependency chain. Default the supplier picker
    # to the one contributing the most components to this order's product, but
    # let the user override to explore other supplier failure scenarios.
    order_suppliers = graph.get_suppliers_for_order(selected_order_id)
    default_supplier = order_suppliers[0][0] if order_suppliers else None

    supplier_options = list(suppliers_df["supplier_id"].unique())
    default_index = supplier_options.index(default_supplier) if default_supplier in supplier_options else 0

    if order_suppliers:
        top_names = ", ".join(f"{s} ({n})" for s, n in order_suppliers[:3])
        st.caption(
            f"**{selected_order_id}** ({selected_order_data['product_name']}) depends on "
            f"{len(order_suppliers)} suppliers. Top by component count: {top_names}. "
            f"Pick one below to see the wider ripple if it slips."
        )

    selected_supplier = st.selectbox(
        "Select Supplier for Impact Analysis:",
        supplier_options,
        index=default_index,
        key="supplier_select",
    )
    
    # Get impact analytics
    impact_analytics, impacted_orders = graph.get_impact_analytics(selected_supplier)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Impact Metrics")
        
        st.metric(
            "Impacted Orders",
            impact_analytics["total_impacted_orders"]
        )
        
        st.metric(
            "Total Impacted Revenue",
            f"${impact_analytics['total_impacted_amount']:,.0f}"
        )
        
        st.metric(
            "At-Risk Orders",
            impact_analytics["delayed_orders"],
            help="Orders in an exception state (On Hold / Back Ordered / Cancelled).",
        )
        
        if len(impacted_orders) > 0:
            st.metric(
                "Average Order Value",
                f"${impact_analytics['avg_order_amount']:,.0f}"
            )
    
    with col2:
        st.markdown("### Impact Distribution")
        
        # Status distribution
        status_dist = pd.DataFrame(
            list(impact_analytics["orders_by_status"].items()),
            columns=["Status", "Count"]
        )
        
        fig = px.bar(
            status_dist,
            x="Status",
            y="Count",
            title="Impacted Orders by Status",
            color_discrete_sequence=["#DC0000"]
        )
        fig.update_layout(plot_bgcolor="rgba(0,0,0,0.05)")
        st.plotly_chart(fig, width='stretch')
    
    st.divider()

    st.markdown("### Impact path — Supplier → Component → Product → Order")
    st.caption(
        f"Nodes and edges reachable from **{selected_supplier}** that lead to "
        f"**{selected_order_id}**. The selected order is highlighted; peer orders on the "
        f"same product are shown in a lighter shade."
    )
    st.plotly_chart(
        _build_impact_diagram(graph, selected_order_id, selected_supplier, orders_df),
        width="stretch",
    )

    st.divider()
    
    st.markdown("### Impacted Orders Details")
    if len(impacted_orders) > 0:
        st.dataframe(
            impacted_orders[["order_id", "customer_id", "product_id", "amount", "status"]].head(10),
            width='stretch'
        )
    else:
        st.info("No impacted orders found for this supplier")
    
    st.divider()
    
    st.markdown("### Cypher Query Example")
    st.code(f"""
MATCH (s:Supplier {{id: '{selected_supplier}'}})
  -[:SUPPLIES]->(c:Component)
  -[:PART_OF]->(p:Product)
  -[:LINKED_TO]->(o:Order)
RETURN
  s.id as supplier,
  COUNT(DISTINCT o) as impacted_orders,
  SUM(o.amount) as total_impact
LIMIT 100;
    """, language="cypher")

# ============================================================================
_boot("UI: tab5 vector")
# TAB 5: VECTOR / AI MODEL
# ============================================================================

with tabs[4]:
    st.markdown("## AI Knowledge Layer (Vector Embeddings)")
    
    st.markdown("### Knowledge Document Retrieval")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Ask AI Assistant")
        
        ai_query = st.text_input(
            "Question:",
            value=f"Why is order {selected_order_data['order_id']} delayed?",
            placeholder="Ask about order delays, supplier issues, etc.",
            label_visibility="collapsed"
        )
        
        if st.button("🔍 Search Knowledge Base"):
            # Pick a plausible supplier ID from the loaded supplier list so the
            # explanation matches the actual data (not a hardcoded "S-123").
            demo_supplier = suppliers_df["supplier_id"].iloc[0] if len(suppliers_df) else None

            summary = vector_engine.get_summary_for_order_delay(
                selected_order_data["order_id"],
                query=ai_query,
                supplier_id=demo_supplier,
            )

            if selected_order_data["status"] not in AT_RISK_STATUSES:
                st.warning(
                    f"Order {selected_order_data['order_id']} is currently "
                    f"'{selected_order_data['status']}' — not in an exception state. "
                    f"The explanation below is illustrative of the retrieval pattern."
                )

            st.markdown("### AI-Generated Explanation")
            st.info(summary["explanation"])

            st.markdown("### Root Cause")
            st.markdown(f"**{summary['root_cause']}**")

            st.markdown("### Confidence Score")
            st.progress(summary["confidence"])

            st.markdown("### Supporting Sources")
            if not summary["supporting_documents"]:
                st.caption("No documents crossed the relevance threshold.")
            for doc in summary["supporting_documents"]:
                with st.expander(f"📄 {doc['source']} (Relevance: {doc['relevance']:.2%})"):
                    st.write(doc["excerpt"])
    
    with col2:
        st.markdown("### Knowledge Document Database")
        
        st.markdown("#### Available Documents:")
        
        docs_info = [
            ("Supplier Bulletin", "supplier_bulletin.txt", "⚠️ Active alerts and supplier status"),
            ("Engineering Notes", "engineering_note.txt", "🔧 Technical constraints and issues"),
            ("Service Manual", "service_manual.txt", "📚 Reference documentation"),
            ("Quality Alerts", "quality_alert.txt", "🚨 Quality and defect reports")
        ]
        
        for doc_name, filename, desc in docs_info:
            st.markdown(f"**{doc_name}**\n\n{desc}")
            if os.path.exists(f"data/documents/{filename}"):
                with open(f"data/documents/{filename}", "r") as f:
                    content = f.read()
                    preview = content[:300] + "..." if len(content) > 300 else content
                    with st.expander(f"View {doc_name}"):
                        st.text(preview)
    
    st.divider()
    
    st.markdown("### Vector Search Technology")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **Method:** TF-IDF (scikit-learn)

        **Features:** unigrams + bigrams, English stop-words

        **Vocab:** up to 5000 features
        """)

    with col2:
        st.markdown("""
        **Similarity:** Cosine Distance

        **Retrieval:** Top-k with threshold

        **Context:** Excerpt extraction
        """)
    
    with col3:
        st.markdown("""
        **Use Cases:**
        - Root cause analysis
        - Knowledge retrieval
        - Anomaly explanation
        - AI assistant backend
        """)

# ============================================================================
_boot("UI: tab6 compare")
# TAB 6: COMPARE — SAME QUESTION, FIVE PARADIGM ANSWERS
# ============================================================================

with tabs[5]:
    st.markdown("## Same question, five paradigm answers")
    st.caption(
        "One realistic supply-chain question, answered against the same underlying "
        "sales orders through each of the five data models. Notice how each paradigm "
        "surfaces something the others cannot."
    )

    st.info(
        "**Business question:** *What is the Q3-2026 exposure from orders in exception states "
        "(On Hold / Back Ordered), and which vendor slips are driving it?*"
    )

    # Shared computation used by every paradigm's card ------------------------
    q3_at_risk = orders_df[
        (orders_df["forecast_quarter"] == "Q3-2026")
        & (orders_df["status"].isin(list(AT_RISK_STATUSES)))
    ]
    q3_delayed = q3_at_risk  # keep alias for downstream code
    delayed_count = len(q3_at_risk)
    delayed_amount = float(q3_at_risk["amount"].sum())

    at_risk_suppliers = suppliers_df[
        suppliers_df["status"].isin(["At Risk", "Probation"])
    ]["supplier_id"].tolist()

    graph_reach = set()
    for sid in at_risk_suppliers:
        graph_reach.update(graph.find_impacted_orders(sid))
    graph_q3 = orders_df[
        orders_df["order_id"].isin(graph_reach)
        & (orders_df["forecast_quarter"] == "Q3-2026")
    ]
    graph_count = len(graph_q3)
    graph_amount = float(graph_q3["amount"].sum())

    vector_hits = vector_engine.search(
        "delayed orders Q3-2026 turbocharger supplier disruption", top_k=1
    )

    # Render each paradigm as a compact card ---------------------------------
    def _paradigm_card(header: str, query_lang: str, query: str, result_md: str, insight: str) -> None:
        with st.container(border=True):
            st.markdown(f"#### {header}")
            st.code(query, language=query_lang)
            st.markdown(result_md)
            st.caption(f"**Unique angle:** {insight}")

    _paradigm_card(
        "1. Relational (3NF) — count them by hand",
        "sql",
        "SELECT COUNT(*) AS at_risk_orders,\n"
        "       SUM(amount) AS at_risk_revenue\n"
        "FROM   SALES_ORDER_HDR\n"
        "WHERE  forecast_quarter = 'Q3-2026'\n"
        "  AND  status IN ('On Hold', 'Back Ordered');",
        f"**Result:** {delayed_count} at-risk orders totalling **${delayed_amount:,.0f}**.",
        "fast and exact for the orders already flagged in exception states — "
        "but nothing about *why*, and no visibility into orders still showing "
        "'Booked' or 'In Production' but sitting behind a failing supplier.",
    )

    with st.container(border=True):
        st.markdown("#### 2. Dimensional (Star Schema) — slice by region and product family")
        st.code(
            "SELECT c.region,\n"
            "       p.product_family,\n"
            "       COUNT(*) AS orders,\n"
            "       SUM(f.amount) AS revenue\n"
            "FROM   FACT_SALES_ORDER f\n"
            "JOIN   DIM_DATE     d ON f.date_key     = d.date_key\n"
            "JOIN   DIM_CUSTOMER c ON f.customer_key = c.customer_key\n"
            "JOIN   DIM_PRODUCT  p ON f.product_key  = p.product_key\n"
            "WHERE  d.quarter = 'Q3-2026'\n"
            "  AND  f.status  IN ('On Hold', 'Back Ordered')\n"
            "GROUP  BY c.region, p.product_family\n"
            "ORDER  BY revenue DESC;",
            language="sql",
        )
        st.markdown("**Result — by region:**")
        region_breakdown = (
            q3_delayed.groupby("region")["amount"]
            .agg(orders="count", revenue="sum")
            .sort_values("revenue", ascending=False)
            .reset_index()
        )
        region_breakdown["revenue"] = region_breakdown["revenue"].map(lambda x: f"${x:,.0f}")
        st.dataframe(region_breakdown, width="stretch", hide_index=True)

        st.markdown("**Result — by product family:**")
        family_breakdown = (
            q3_delayed.groupby("product_family")["amount"]
            .agg(orders="count", revenue="sum")
            .sort_values("revenue", ascending=False)
            .reset_index()
        )
        family_breakdown["revenue"] = family_breakdown["revenue"].map(lambda x: f"${x:,.0f}")
        st.dataframe(family_breakdown, width="stretch", hide_index=True)

        st.caption(
            "**Unique angle:** decomposes the same number into the three KPI dimensions "
            "any BI report asks for — Customer (region), Product (family), Time (quarter). "
            "Pre-joined for BI speed."
        )

    _paradigm_card(
        "3. Semi-Structured (JSON) — pull the messy attributes",
        "json",
        "// MongoDB-style aggregation\n"
        "db.orders.aggregate([\n"
        "  { $match: { forecast_quarter: 'Q3-2026', status: { $in: ['On Hold', 'Back Ordered'] } } },\n"
        "  { $project: { order_id: 1,\n"
        "                shipping: 1,\n"
        "                engine_options: 1,\n"
        "                'metadata.compliance_flags': 1 } }\n"
        "]);",
        f"**Result:** {delayed_count} documents, each carrying variable shipping / "
        f"engine-options / compliance-flag payloads that never fit tidily in relational columns.",
        "the only paradigm that captures the *shape variance* of real orders — expedited "
        "shipping, custom engine options, export-control flags — without schema changes.",
    )

    _paradigm_card(
        "4. Graph — expand from at-risk suppliers",
        "cypher",
        "MATCH (s:Supplier)-[:SUPPLIES]->(c:Component)\n"
        "     -[:PART_OF]->(p:Product)\n"
        "     -[:LINKED_TO]->(o:Order)\n"
        "WHERE s.status IN ['At Risk', 'Probation']\n"
        "  AND o.forecast_quarter = 'Q3-2026'\n"
        "RETURN COUNT(DISTINCT o) AS reachable_orders,\n"
        "       SUM(o.amount)     AS exposure;",
        f"**Result:** {graph_count} orders totalling **${graph_amount:,.0f}** are "
        f"downstream of the {len(at_risk_suppliers)} suppliers currently flagged "
        f"At Risk / Probation — even the ones still showing 'Booked' or 'In Production'.",
        "surfaces *latent* risk. The relational answer stops at explicit exception statuses; "
        "the graph answer walks the dependency chain and finds orders that will slip.",
    )

    with st.container(border=True):
        st.markdown("#### 5. Vector / AI — ask in natural language")
        st.code(
            'search("delayed orders Q3-2026 turbocharger supplier disruption", top_k=1)',
            language="python",
        )
        if vector_hits:
            doc = vector_hits[0]
            st.markdown(
                f"**Top match:** *{doc['metadata']['doc_type']}* "
                f"(relevance {doc['similarity_score']:.0%})"
            )
            st.markdown(f"> {doc['excerpt']}")
        else:
            st.markdown("_(No high-relevance match found in the knowledge base.)_")
        st.caption(
            "**Unique angle:** answers *why* the delays are happening by pulling the "
            "relevant supplier bulletins, quality alerts and engineering notes into context."
        )

    st.divider()
    st.markdown(
        "**Bottom line:** no single paradigm answers this question completely. "
        "Relational tells you the current state; dimensional tells you where; "
        "JSON captures the messy detail; graph exposes latent risk; vector explains the cause. "
        "Prism keeps all five projections in sync from one canonical sales order."
    )

# ============================================================================
_boot("UI: tab7 ask")
# TAB 7: ASK — LLM-ORCHESTRATED CHAT OVER ALL FIVE PARADIGMS
# ============================================================================

with tabs[6]:
    st.markdown("## Ask Prism — one question, five paradigms")
    st.caption(
        "Type any question about the sales orders. An LLM decides which of the "
        "five paradigms to consult — relational, dimensional, JSON, graph, or "
        "vector — runs the queries on your behalf, and synthesises an answer "
        "grounded in what each paradigm returned."
    )

    _orchestrator_config = OrchestratorConfig()
    if not _orchestrator_config.is_ready():
        missing = ", ".join(_orchestrator_config.missing())
        st.warning(
            f"Chat is disabled — the following Azure OpenAI credentials are not "
            f"configured: **{missing}**. Locally, add them to a `.env` file. On "
            f"Streamlit Cloud, add them under **Manage app → Settings → Secrets**."
        )
    else:
        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        # Render prior conversation
        for turn in st.session_state.chat_history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])
                if turn["role"] == "assistant" and turn.get("tool_calls"):
                    with st.expander(f"🔧 Paradigms consulted ({len(turn['tool_calls'])})"):
                        for tc in turn["tool_calls"]:
                            st.markdown(f"**{tc['name']}** — args `{tc['arguments']}`")
                            st.json(tc["result"])

        # Prompt row
        col_input, col_reset = st.columns([5, 1])
        with col_input:
            user_prompt = st.chat_input(
                "e.g. 'How exposed are we from Supplier-S005 delays this quarter?'"
            )
        with col_reset:
            if st.button("Reset chat", use_container_width=True):
                st.session_state.chat_history = []
                st.rerun()

        if user_prompt:
            st.session_state.chat_history.append({"role": "user", "content": user_prompt})
            with st.chat_message("user"):
                st.markdown(user_prompt)
            with st.chat_message("assistant"):
                with st.spinner("Consulting the five paradigms…"):
                    orch = PrismOrchestrator(orders_df, graph, vector_engine, _orchestrator_config)
                    resp = orch.ask(user_prompt)
                if resp.error:
                    st.error(resp.error)
                    st.session_state.chat_history.append(
                        {"role": "assistant", "content": f"Error: {resp.error}", "tool_calls": []}
                    )
                else:
                    st.markdown(resp.answer)
                    if resp.tool_calls:
                        with st.expander(f"🔧 Paradigms consulted ({len(resp.tool_calls)})"):
                            for tc in resp.tool_calls:
                                st.markdown(f"**{tc.name}** — args `{tc.arguments}`")
                                st.json(tc.result)
                    st.session_state.chat_history.append({
                        "role": "assistant",
                        "content": resp.answer,
                        "tool_calls": [
                            {"name": tc.name, "arguments": tc.arguments, "result": tc.result}
                            for tc in resp.tool_calls
                        ],
                    })

    st.divider()
    st.caption(
        "*Suggested prompts:* "
        "'How much revenue is exposed to Q3-2026 delays?' · "
        "'Which supplier is putting the most orders at risk?' · "
        "'Explain why CAT 3500 engines are behind schedule.'"
    )

# ============================================================================
_boot("UI: tab8 agents")
# TAB 8: AGENTS — MULTI-AGENT SQUAD (ROUTER + 5 SPECIALISTS + SYNTHESISER)
# ============================================================================

with tabs[7]:
    st.markdown("## Agent Squad — one Router, five specialists, one Synthesiser")
    st.caption(
        "Where the **Ask** tab uses a single LLM juggling all five tools, this tab "
        "shows the *agent-per-domain* pattern: a Router LLM decomposes the question, "
        "dispatches focused sub-questions to five specialist LLMs (each with access "
        "to only its own paradigm's tool), then a Synthesiser LLM combines the "
        "findings into one grounded answer. More LLM calls per question, but every "
        "collaboration step is visible."
    )

    with st.expander("Meet the specialists"):
        for prof in SPECIALISTS.values():
            st.markdown(f"**{prof.name}** — {prof.role}")

    _sq_config = OrchestratorConfig()
    if not _sq_config.is_ready():
        missing = ", ".join(_sq_config.missing())
        st.warning(
            f"Multi-agent mode is disabled — missing credentials: **{missing}**."
        )
    else:
        if "squad_history" not in st.session_state:
            st.session_state.squad_history = []

        # Prior turns
        for turn in st.session_state.squad_history:
            with st.chat_message(turn["role"]):
                st.markdown(turn["content"])
                if turn["role"] == "assistant" and turn.get("plan"):
                    with st.expander(
                        f"🧭 Router's plan · {len(turn['plan'])} specialists dispatched"
                    ):
                        st.markdown(f"*Rationale:* {turn.get('rationale', '(none)')}")
                        for step in turn["plan"]:
                            st.markdown(
                                f"- **{SPECIALISTS[step['specialist']].name}** — "
                                f"{step['sub_question']}"
                            )
                    for outcome in turn.get("outcomes", []):
                        with st.expander(
                            f"🔍 {outcome['specialist_name']} · used `{outcome['tool_name']}`"
                        ):
                            st.markdown(f"**Sub-question:** {outcome['sub_question']}")
                            st.markdown(f"**Tool arguments:** `{outcome['tool_arguments']}`")
                            st.markdown("**Tool result:**")
                            st.json(outcome["tool_result"])
                            st.markdown(f"**Finding:** {outcome['finding']}")

        col_input, col_reset = st.columns([5, 1])
        with col_input:
            squad_prompt = st.chat_input(
                "e.g. 'Which region carries the most Q3 delay revenue, and why?'",
                key="squad_input",
            )
        with col_reset:
            if st.button("Reset squad", use_container_width=True, key="reset_squad"):
                st.session_state.squad_history = []
                st.rerun()

        if squad_prompt:
            st.session_state.squad_history.append(
                {"role": "user", "content": squad_prompt}
            )
            with st.chat_message("user"):
                st.markdown(squad_prompt)
            with st.chat_message("assistant"):
                with st.spinner("Router planning → specialists working → Synthesiser writing…"):
                    squad = PrismAgentSquad(orders_df, graph, vector_engine, _sq_config)
                    resp = squad.ask(squad_prompt)
                if resp.error:
                    st.error(f"Agent squad failed: {resp.error}")
                    st.session_state.squad_history.append({
                        "role": "assistant",
                        "content": f"Error: {resp.error}",
                        "plan": [], "rationale": "", "outcomes": [],
                    })
                else:
                    st.markdown(resp.final_answer)
                    if resp.plan:
                        with st.expander(
                            f"🧭 Router's plan · {len(resp.plan)} specialists dispatched"
                        ):
                            st.markdown(f"*Rationale:* {resp.plan_rationale or '(none)'}")
                            for step in resp.plan:
                                st.markdown(
                                    f"- **{SPECIALISTS[step['specialist']].name}** — "
                                    f"{step['sub_question']}"
                                )
                    for outcome in resp.outcomes:
                        with st.expander(
                            f"🔍 {outcome.specialist_name} · used `{outcome.tool_name}`"
                        ):
                            st.markdown(f"**Sub-question:** {outcome.sub_question}")
                            st.markdown(f"**Tool arguments:** `{outcome.tool_arguments}`")
                            st.markdown("**Tool result:**")
                            st.json(outcome.tool_result)
                            st.markdown(f"**Finding:** {outcome.finding}")

                    st.session_state.squad_history.append({
                        "role": "assistant",
                        "content": resp.final_answer,
                        "plan": resp.plan,
                        "rationale": resp.plan_rationale,
                        "outcomes": [
                            {
                                "specialist_name": o.specialist_name,
                                "sub_question": o.sub_question,
                                "tool_name": o.tool_name,
                                "tool_arguments": o.tool_arguments,
                                "tool_result": o.tool_result,
                                "finding": o.finding,
                            }
                            for o in resp.outcomes
                        ],
                    })

    st.divider()
    st.caption(
        "Expect ~5–10 seconds per question — this tab makes multiple LLM calls "
        "(1 planning + N specialists + 1 synthesis). The Ask tab is faster; this "
        "tab shows more of the collaboration."
    )

# ---- Platform stats (ambient, small strip near footer) ---------------------
_boot("UI: platform stats")

st.divider()
st.caption("Platform snapshot")

stat_cols = st.columns(5)
stat_data = [
    ("Sales Orders", len(orders_df)),
    ("Dealers", orders_df["customer_id"].nunique()),
    ("Products", orders_df["product_id"].nunique()),
    ("Suppliers", len(suppliers_df)),
    ("Components", len(set(graph_edges_df[graph_edges_df["relationship"] == "supplies"]["target"]))),
]
for col, (label, value) in zip(stat_cols, stat_data):
    col.metric(label=label, value=f"{value:,}")

# ---- Footer -----------------------------------------------------------------
_boot("UI: footer")

st.markdown(
    f'<p style="text-align:center;color:#8a8a8a;font-size:0.8rem;margin-top:2rem;">'
    f'Prism Multi-Model Framework Demonstrator · Synthetic data · '
    f'{datetime.now().strftime("%Y-%m-%d")}'
    f'</p>',
    unsafe_allow_html=True,
)
