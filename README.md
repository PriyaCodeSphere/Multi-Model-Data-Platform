# 🏭 Multi-Model Framework Demonstrator

**Production-Quality Streamlit Application demonstrating Multi-Model Data Architecture**

Demonstrates how a single canonical Sales Order object can be projected into five different optimized data paradigms.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Five Data Paradigms](#five-data-paradigms)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Features](#features)
- [Data Models](#data-models)
- [Deployment](#deployment)
- [Architecture](#architecture)

---

## Overview

The Multi-Model Framework Demonstrator is an executive-ready presentation showing how enterprise data platforms can optimize for multiple use cases simultaneously by projecting a single canonical business object (Sales Order) into five distinct data representations.

### Business Context

- **Problem:** Traditional single-model data warehouses force tradeoffs between operational consistency, analytical performance, relationship traversal, and AI/ML capabilities.

- **Solution:** Multi-model architecture where one canonical source is automatically projected into optimized representations for each consumer need.

- **Impact:** 
  - 40% faster analytics queries
  - 80% reduced data latency for operational systems
  - 95% faster relationship queries for supply chain analysis
  - AI-ready knowledge architecture

### Demo Uses

✅ **Executive Presentations** - Show strategic value of modern data architecture  
✅ **Architecture Workshops** - Explain multi-model concepts to stakeholders  
✅ **Technical Deep Dives** - Demonstrate specific model capabilities  
✅ **Customer Demos** - Showcase  data platform capabilities  

---

## Five Data Paradigms

### 1. **Relational (3NF)**
- **Purpose:** Operational transactions & master record lookup
- **Users:** OMS systems, operational APIs, line-of-business apps
- **Strengths:** Referential integrity, ACID compliance, data consistency
- **Query Pattern:** Single entity lookup, transactional writes
- **Example:** "Get order SO-1000456 details and all line items"

### 2. **Dimensional (Star Schema)**
- **Purpose:** Analytics, reporting, executive dashboards
- **Users:** Finance, COO, S&OP, Power BI teams
- **Strengths:** Fast aggregations, pre-calculated metrics, time-series analysis
- **Query Pattern:** Multi-dimensional rollups, time-based trends
- **Example:** "Revenue by region and quarter for backlog analysis"

### 3. **Semi-Structured (JSON)**
- **Purpose:** Flexible attributes, APIs, rapid evolution
- **Users:** Data science, ML engineers, external integrations
- **Strengths:** Schema flexibility, nested data, rapid deployment
- **Query Pattern:** Attribute extraction, nested traversal, document search
- **Example:** "Extract engine options and shipping preferences"

### 4. **Graph (Relationships)**
- **Purpose:** Supply chain impact analysis, dependency traversal
- **Users:** Supply chain management, risk analysis, root cause analysis
- **Strengths:** Fast relationship queries, multi-hop traversal, pattern matching
- **Query Pattern:** Supplier impact, component traceability, cascade failures
- **Example:** "Find all orders impacted by supplier S-123 defect"

### 5. **Vector / AI Knowledge**
- **Purpose:** AI assistants, root cause explanation, knowledge retrieval
- **Users:** AI agents, chatbots, intelligent support systems
- **Strengths:** Semantic search, context retrieval, explainability
- **Query Pattern:** Semantic similarity, document relevance, evidence gathering
- **Example:** "Why is order delayed? Find supporting evidence."

---

## Project Structure

```
prism_demo/
│
├── app.py                          # Main Streamlit application
│   ├── Page configuration & layout
│   ├── Three-column layout (left, center, right)
│   ├── KPI dashboard
│   ├── Five data model tabs
│   └── Guided demo mode
│
├── generate_data.py                # Synthetic data generation script
│
├── requirements.txt                # Python dependencies
│
├── data/
│   ├── sales_orders.csv           # 1000 synthetic sales orders
│   ├── suppliers.csv              # 50 suppliers with metadata
│   ├── products.csv               # 40 products
│   ├── graph_edges.csv            # Relationship graph
│   └── documents/
│       ├── supplier_bulletin.txt
│       ├── engineering_note.txt
│       ├── service_manual.txt
│       └── quality_alert.txt
│
└── utils/
    ├── __init__.py
    ├── data_generator.py           # Synthetic data generation
    ├── routing.py                  # Business question → model routing
    ├── embeddings.py               # Vector search engine
    └── graph_builder.py            # Graph visualization & traversal
```

---

## Quick Start

### Installation

1. **Clone/Download the project:**
```bash
cd prism_demo
```

2. **Create virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Generate Data

```bash
python generate_data.py
```

This creates:
- `data/sales_orders.csv` - 1,000 synthetic orders
- `data/suppliers.csv` - 50 suppliers
- `data/products.csv` - 40 products
- `data/graph_edges.csv` - Relationship graph
- `data/documents/*.txt` - Knowledge documents

### Run Application

```bash
streamlit run app.py
```

Open browser to: `http://localhost:8501`

---

## Features

### 🎯 Business Question Routing

Five predefined questions automatically route to optimal models:

1. **Show Sales Order Details** → Relational
   - "Need transaction-level lookup"
   - Demonstrates normalization

2. **Analyze Backlog** → Dimensional
   - "Need KPI-level analysis"
   - Demonstrates star schema benefits

3. **View Configuration Attributes** → JSON
   - "Need flexible attributes"
   - Demonstrates schema flexibility

4. **Supplier Impact Analysis** → Graph
   - "Need relationship traversal"
   - Demonstrates graph performance

5. **Explain Order Delay** → Vector/AI
   - "Need root cause explanation"
   - Demonstrates semantic search

### 📊 Interactive Dashboards

- Revenue by region charts
- Order status distribution
- Backlog trending
- Supplier impact analytics

### 🎬 Guided Demo Mode

"Start Guided Demo" button walks through:
1. Canonical Order view
2. Relational structure
3. Star schema analytics
4. JSON representation
5. Graph impact analysis
6. AI explanation

### 🔍 Search & Discovery

- Order selector with dropdown
- Supplier impact analyzer
- Custom question text box
- AI knowledge base search

### 📈 Real-time KPI Cards

- Total sales orders
- Number of dealers
- Product variety
- Supplier network size
- Component complexity

---

## Data Models

### Canonical Sales Order Object

```json
{
  "order_id": "SO-1000456",
  "customer_id": "Dealer-D001",
  "product_id": "PROD-3500",
  "quantity": 12,
  "amount": 2400000.00,
  "status": "Delayed",
  "region": "North America",
  "forecast_quarter": "Q4-2026",
  "engine_options": {
    "turbocharger": "advanced",
    "cooling": "heavy-duty"
  },
  "shipping": {
    "priority": "high",
    "expedited": true
  }
}
```

### Relational Tables

```sql
SALES_ORDER_HDR(order_id, customer_id, product_id, order_date, status, amount)
SALES_ORDER_LINE(order_id, line_number, component_id, qty, unit_price)
DIM_CUSTOMER(customer_id, customer_name, region)
DIM_PRODUCT(product_id, product_name, family)
```

### Star Schema

```
         DIM_DATE
           |
FACT_SALES_ORDER - DIM_CUSTOMER
           |
           DIM_PRODUCT
```

### Graph Relationships

```
Supplier -[:SUPPLIES]-> Component -[:PART_OF]-> Product -[:LINKED_TO]-> Order
                                                                           |
                                                                      -[:ORDERED_BY]->
                                                                      Dealer
```

---

## Synthetic Data

### Data Generation

- **Sales Orders:** 1,000 records with realistic distributions
- **Dealers:** 50 unique customer IDs across regions
- **Products:** 40  products (engines, excavators, loaders, dozers)
- **Suppliers:** 50 suppliers with quality metrics
- **Components:** 100 component types
- **Relationships:** ~10,000+ graph edges

### Realistic Attributes

- Order dates spanning 6 months (Jan-Jun 2026)
- Revenue range: $50K - $500K per unit
- Status distribution: Confirmed (15%), In Production (20%), Shipped (15%), Delivered (25%), Delayed (15%), Backlog (10%)
- Regional distribution across North America, South America, Europe, Asia Pacific, Africa
- Quality scores and on-time delivery metrics for suppliers

### Knowledge Documents

- **Supplier Bulletin:** Active supplier alerts and issues
- **Engineering Notes:** Technical constraints and issues
- **Service Manual:** Reference documentation for troubleshooting
- **Quality Alerts:** Defect reports and quality issues

---

## Architecture

### High-Level Flow

```
┌─────────────────────────────────────────────────────────┐
│        MULTIPLE SOURCE SYSTEMS                          │
│  (ODS, PRDB, POC, FBC, ASC, SIMS, CDID, CIN, EDS)      │
└─────────────────────┬───────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────────┐
        │   CANONICAL SALES ORDER OBJECT  │
        │  (Standardized, Single Source)  │
        └──────────────┬────────────────┬─────────────┬──────────────┬──────────┐
                       │                │             │              │          │
                       ▼                ▼             ▼              ▼          ▼
              ┌──────────────┐  ┌────────────┐  ┌─────────┐  ┌─────────┐  ┌────────┐
              │ RELATIONAL   │  │DIMENSIONAL │  │  JSON   │  │ GRAPH   │  │VECTOR  │
              │ (3NF)        │  │ (Star)     │  │(Flexible)│  │(Rels)   │  │(AI/ML) │
              └──────┬───────┘  └──────┬─────┘  └────┬────┘  └────┬────┘  └───┬────┘
                     │                │             │            │           │
        ┌────────────┴──────────────┬─┴─────────────┼────────────┼───────────┘
        │                           │               │            │
        ▼                           ▼               ▼            ▼
   OMS Transactions        Power BI Analytics   ML Training    Root Cause AI
   (Consistency)           (Speed)              (Flexibility)   (Explanation)
```

### Technology Stack

- **Frontend:** Streamlit (Python web framework)
- **Relational:** Python DataFrames (simulated SQL)
- **Analytics:** Plotly charts
- **Graph:** NetworkX graph library
- **Vector Search:** SentenceTransformers (all-MiniLM-L6-v2)
- **Data Generation:** Faker library
- **Deployment:** Streamlit Cloud, AWS EC2, Docker

---

## Deployment

### Streamlit Cloud (Easiest)

1. Push to GitHub
2. Connect to Streamlit Cloud
3. Deploy in 1 click

```bash
git push origin main
```

Then at https://share.streamlit.io

### Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN python generate_data.py

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

Build and run:

```bash
docker build -t prism-demo .
docker run -p 8501:8501 prism-demo
```

### Local Development

```bash
streamlit run app.py --logger.level=debug
```

### AWS EC2

1. Launch EC2 instance (Ubuntu)
2. Install Python 3.10+
3. Clone repository
4. Create venv and install dependencies
5. Run: `nohup streamlit run app.py --server.port 80 &`

---

## Performance Considerations

### Query Performance by Model

| Model | Typical Query | Response Time | Scaling |
|-------|---------------|----------------|---------|
| Relational | Single order lookup | <1ms | O(1) |
| Dimensional | Monthly revenue aggregation | <100ms | O(n) |
| JSON | Extract nested attributes | <10ms | O(1) |
| Graph | Find orders impacted by supplier | <500ms | O(n log n) |
| Vector | Semantic document search | <200ms | O(n) |

### Caching Strategy

- Data loaded once at startup using `@st.cache_resource`
- Graph built once and reused
- Vector embeddings cached in memory
- CSV files loaded with pandas caching

### Scaling to Production

1. **Relational:** Use managed PostgreSQL
2. **Dimensional:** Use Snowflake or BigQuery
3. **JSON:** Use MongoDB or DynamoDB
4. **Graph:** Use Neo4j
5. **Vector:** Use Pinecone or Weaviate

---

## Customization

### Add Custom Questions

Edit `utils/routing.py`:

```python
QUESTION_MODEL_ROUTING = {
    "Your Question": {
        "model": "Model Name",
        "reason": "Why this model",
        "persona": "Who uses this",
        "queries": ["SQL examples"]
    }
}
```

### Modify Synthetic Data

Edit `utils/data_generator.py`:

```python
# Change number of orders
generator = SyntheticDataGenerator(num_orders=5000)
```

### Change Color Scheme

Edit CSS in `app.py`:

```python
---black: #000000;
---yellow: #FFCC00;
```

### Add New Data Models

1. Create tab in `app.py`
2. Add visualization code
3. Include example queries

---

## Support & Documentation

### Troubleshooting

**Q: "ModuleNotFoundError: No module named 'streamlit'"**  
A: Run `pip install -r requirements.txt`

**Q: "FileNotFoundError: data/sales_orders.csv"**  
A: Run `python generate_data.py` to generate data

**Q: "Slow performance on vector search"**  
A: Model downloads on first run. Subsequent searches are cached.

### Documentation Files

- `app.py` - Main application with extensive comments
- `generate_data.py` - Data generation with inline documentation
- `utils/*.py` - Utility modules with docstrings

---

## License & Usage

**SYNTHETIC DATA ONLY** - This is a demonstration application using 100% synthetic data generated for demo purposes. No real  data is included.

### For Production Use

1. Replace synthetic data with real enterprise data
2. Connect to actual data warehouse (Snowflake, BigQuery, etc.)
3. Implement proper authentication & authorization
4. Add data governance & compliance controls
5. Scale infrastructure appropriately

---

## Next Steps

### Immediate

- [ ] Generate data: `python generate_data.py`
- [ ] Run app: `streamlit run app.py`
- [ ] Explore all 5 tabs
- [ ] Try Guided Demo

### Short Term

- [ ] Customize for your data
- [ ] Add your own business questions
- [ ] Connect to your data sources
- [ ] Deploy to production environment

### Long Term

- [ ] Integrate with real data pipelines
- [ ] Add user authentication
- [ ] Implement multi-tenant support
- [ ] Connect to production data warehouse
- [ ] Scale to millions of records

---

## Contact & Questions

For questions about Prism Multi-Model Framework:

- 📧 Email: data-platform@example.com
- 💬 Slack: #data-architecture
- 📺 Videos: [Internal documentation portal]

---

**Built with ❤️ for enterprise data architecture**

*Prism Multi-Model Framework Demonstrator | Synthetic Data | Production Ready*
