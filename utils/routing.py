"""
Routing Logic: Maps Business Questions to Optimal Data Models
"""

QUESTION_MODEL_ROUTING = {
    "Show Sales Order Details": {
        "model": "Relational",
        "reason": "Master record lookup requires normalized structure for data integrity and referential consistency",
        "persona": "OMS Team / Operational APIs",
        "queries": [
            "SELECT order_id, customer_id, product_id, status FROM sales_orders WHERE order_id = ?",
            "SELECT * FROM order_lines WHERE order_id = ?",
            "SELECT * FROM order_history WHERE order_id = ? ORDER BY timestamp DESC"
        ]
    },
    "Analyze Backlog": {
        "model": "Dimensional (Star Schema)",
        "reason": "Optimized for aggregate reporting and KPI analysis across multiple dimensions",
        "persona": "COO / Finance / S&OP",
        "queries": [
            "SELECT region, status, COUNT(*) as orders, SUM(amount) as total FROM fact_orders GROUP BY region, status",
            "SELECT forecast_quarter, COUNT(*) as backlog_count, SUM(amount) as backlog_value FROM fact_orders WHERE status='Backlog' GROUP BY forecast_quarter",
            "SELECT customer_id, SUM(amount) as backlog_value FROM fact_orders WHERE status='Backlog' GROUP BY customer_id ORDER BY backlog_value DESC"
        ]
    },
    "View Configuration Attributes": {
        "model": "Semi-Structured (JSON)",
        "reason": "Schema flexibility enables rapid evolution and variable attributes per product",
        "persona": "Data Science / AI/ML / External APIs",
        "queries": [
            "SELECT order_json->'engine_options' as options FROM sales_orders_json WHERE order_id = ?",
            "SELECT order_json->'promo_codes' as promotions FROM sales_orders_json",
            "SELECT DISTINCT order_json->'shipping'->>'priority' as priority_levels FROM sales_orders_json"
        ]
    },
    "Supplier Impact Analysis": {
        "model": "Graph",
        "reason": "Relationship traversal across suppliers, components, machines and orders",
        "persona": "Supply Chain / Risk Management",
        "queries": [
            "MATCH (s:Supplier)-[:SUPPLIES]->(c:Component)-[:PART_OF]->(p:Product)-[:LINKED_TO]->(o:Order) WHERE s.id = ? RETURN o",
            "MATCH (s:Supplier)-[*1..3]-(o:Order) WHERE s.id = ? RETURN count(DISTINCT o) as impacted_orders",
            "MATCH (s:Supplier)-[:SUPPLIES]->(c:Component) WHERE s.quality_score < 0.9 RETURN s.id, c.id, c.type"
        ]
    },
    "Explain Order Delay": {
        "model": "Vector / AI Knowledge",
        "reason": "Retrieve contextual information from knowledge documents for root cause analysis",
        "persona": "AI Assistants / Agents / Knowledge Workers",
        "queries": [
            "SEARCH documents FOR 'turbocharger delay' WITH similarity > 0.8",
            "SEARCH documents FOR supplier disruptions related to order components",
            "SEARCH quality_alerts FOR issues matching order_id components"
        ]
    }
}

def get_model_recommendation(question):
    """Get model recommendation for a business question"""
    if question in QUESTION_MODEL_ROUTING:
        return QUESTION_MODEL_ROUTING[question]
    return None

def get_all_questions():
    """Get list of all business questions"""
    return list(QUESTION_MODEL_ROUTING.keys())

def route_question_to_model(question):
    """Route question to recommended model"""
    recommendation = get_model_recommendation(question)
    if recommendation:
        return recommendation["model"]
    return None
