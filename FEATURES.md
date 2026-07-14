# 🌟 Prism Multi-Model Framework Demonstrator - Features

## Core Features

### 1. **Five Data Paradigm Projections**

#### Relational (3NF)
- **Tab:** "1️⃣ Relational"
- **Shows:** Normalized table structures
- **Tables:**
  - SALES_ORDER_HDR (master records)
  - SALES_ORDER_LINE (line items)
  - Sample queries with actual SQL
- **Use Case:** "Show order details, master record lookup"
- **Personas:** OMS Team, Operational APIs
- **Performance:** <1ms lookups
- **Sample Query:**
  ```sql
  SELECT * FROM SALES_ORDER_HDR 
  WHERE order_id = 'SO-1000456'
  ```

#### Dimensional (Star Schema)
- **Tab:** "2️⃣ Dimensional"
- **Shows:** Fact and dimension tables
- **Dimensions:**
  - DIM_CUSTOMER (regions, dealers)
  - DIM_DATE (time dimensions)
  - DIM_PRODUCT (product families)
- **Visualizations:**
  - Revenue by region (bar chart)
  - Orders by status (pie chart)
  - Interactive Plotly charts
- **Use Case:** "Analyze backlog, revenue trends"
- **Personas:** COO, Finance, S&OP
- **Performance:** <100ms aggregations
- **Automatic Features:**
  - Real-time aggregations from data
  - Color-coded status distribution
  - Regional breakdown

#### Semi-Structured (JSON)
- **Tab:** "3️⃣ JSON"
- **Shows:** Flexible document structure
- **Includes:**
  - Engine options (turbocharger, cooling)
  - Shipping preferences (priority, expedited)
  - Metadata (created_at, source_system)
  - Promotion codes
- **Expandable:** Click to expand/collapse sections
- **Syntax:** Highlighted JSON viewing
- **Use Case:** "View configuration attributes, external APIs"
- **Personas:** Data science, ML engineers
- **Performance:** <10ms attribute extraction
- **Benefits Highlighted:**
  - Schema flexibility
  - Rapid evolution
  - Variable attributes

#### Graph (Relationships)
- **Tab:** "4️⃣ Graph"
- **Shows:** Relationship traversal and impact analysis
- **Key Feature:** **Supplier Impact Analysis**
  - Select supplier from dropdown
  - Automatically calculates:
    - Total impacted orders
    - Total impacted revenue
    - Affected regions
    - Affected products
    - Affected customers
    - Orders by status
  - Displays complete list of impacted orders
- **Relationships Shown:**
  - Supplier -[:SUPPLIES]-> Component
  - Component -[:PART_OF]-> Product
  - Product -[:LINKED_TO]-> Order
  - Order -[:ORDERED_BY]-> Dealer
- **Cypher Example:** Displays actual Neo4j-style queries
- **Use Case:** "Supplier impact analysis, root cause analysis"
- **Personas:** Supply chain management, risk team
- **Performance:** <500ms traversal
- **Metrics:**
  - Number of impacted orders
  - Revenue impact
  - Regional impact
  - Status breakdown

#### Vector / AI Knowledge
- **Tab:** "5️⃣ Vector/AI"
- **Shows:** Semantic search and AI explanations
- **Components:**
  - Search box for questions
  - Document database (4 knowledge documents)
  - Similarity scoring (0-1)
  - Root cause analysis
  - Supporting evidence
- **Search Features:**
  - Semantic similarity matching
  - Relevance scoring
  - Multi-document results
  - Excerpt extraction
- **AI Capabilities:**
  - Root cause generation
  - Confidence scoring
  - Supporting document citation
  - Explanation generation
- **Knowledge Base:**
  - supplier_bulletin.txt (active alerts)
  - engineering_note.txt (technical constraints)
  - service_manual.txt (reference docs)
  - quality_alert.txt (defect reports)
- **Use Case:** "Explain order delay, knowledge retrieval"
- **Personas:** AI assistants, support teams
- **Performance:** 200-500ms first search, <50ms cached
- **Example Question:** "Why is order SO-1000456 delayed?"
- **Example Answer:** "Turbocharger shortage from Supplier S-123 (confidence: 85%)"

---

### 2. **Automatic Business Question Routing**

Demonstrates how different business questions route to different models:

| Question | Model | Reason | Persona |
|----------|-------|--------|---------|
| Show Sales Order Details | Relational | Master record lookup | OMS Team |
| Analyze Backlog | Dimensional | KPI-level aggregation | Finance |
| View Configuration Attributes | JSON | Schema flexibility | Data Science |
| Supplier Impact Analysis | Graph | Relationship traversal | Supply Chain |
| Explain Order Delay | Vector/AI | Semantic knowledge retrieval | AI Agents |

**Features:**
- Question dropdown selector
- Automatic model recommendation
- Reason displayed
- Persona identified
- Sample queries shown
- Custom question textbox

---

### 3. **Interactive Dashboard**

#### Top KPI Cards
Five metric cards display:
- **📦 Sales Orders** (1,000 synthetic)
- **🏭 Dealers** (50 unique customers)
- **🛠️ Products** (10 product types)
- **🤝 Suppliers** (20 supplier network)
- **⚙️ Components** (100+ components)

Color scheme:
-  black background
-  yellow text
- Real-time calculation from data

#### Three-Column Layout

**Left Panel: Business Questions**
- Dropdown with 5 predefined questions
- Custom question textbox
- Question details display
- Sample SQL queries
- Persona information

**Center Panel: Canonical Sales Order**
- Order selector dropdown
- Order summary display
- Key attributes highlighted:
  - Order ID
  - Customer
  - Product
  - Quantity
  - Region
  - Amount
  - Status
  - Forecast quarter
- JSON representation (expandable)
- Beautiful formatting

**Right Panel: Model Recommendation**
- Shows selected question
- Recommended model
- Reasoning
- Best for (personas)
- All model paradigms listed

---

### 4. **Guided Demo Mode**

**Feature: "🎬 Start Guided Demo" Button**

Walks users through entire data journey:

1. **Canonical Order** - View the source truth
2. **Relational View** - See normalized structure
3. **Star View** - Analytics optimization
4. **JSON View** - Flexible representation
5. **Graph View** - Relationship analysis
6. **AI Explanation** - Knowledge retrieval

**UI Elements:**
- Previous/Next navigation
- Progress bar
- Step counter (Step 1/6)
- Clear step description
- Auto-scroll to relevant content

**Perfect For:**
- Customer presentations
- Training new team members
- Sales demos
- Architecture workshops

---

### 5. **Synthetic Data Generation**

**Realistic Dataset:**
- **1,000 sales orders** with:
  - Order IDs (SO-1000000 to SO-1000999)
  - Realistic order dates (6-month span)
  - Revenue $50K to $500K per unit
  - Multiple status values
  - Regional distribution
  - Product assignments

- **20 suppliers** with:
  - Quality scores (0.85-0.99)
  - On-time delivery metrics
  - Status (Active, At Risk, Probation)
  - Country of origin

- **10 products** including:
  - Engines (CAT 3500, 3600)
  - Excavators (CAT 380, 390, 320)
  - Loaders (CAT 950, 980)
  - Dozers (CAT D10, D9, D6)

- **100 components** (COMP-0001 to COMP-0100)

- **2,200+ relationships:**
  - Supplier supplies component
  - Component belongs to product
  - Product linked to order
  - Order ordered by customer

- **4 knowledge documents:**
  - Supplier bulletins
  - Engineering notes
  - Service manuals
  - Quality alerts

---

### 6. **Data Visualization**

#### Plotly Charts
- Revenue by Region (bar chart)
  - Interactive hover
  - Download as PNG
  - Color-coded
- Orders by Status (pie chart)
  - Status breakdown
  - Percentage display
  - Interactive labels

#### Status Distribution
- Realistic distribution:
  - Confirmed: 15%
  - In Production: 20%
  - Shipped: 15%
  - Delivered: 25%
  - Delayed: 15%
  - Backlog: 10%

#### Interactive Tables
- Sortable columns
- Expandable rows
- Data export capability
- Pagination support

---

### 7. **Supplier Impact Analysis (Graph Model Highlight)**

**This is the WOW factor of the demo!**

**How it works:**

1. Select any supplier from dropdown
2. Application instantly:
   - Traverses graph relationships
   - Finds all components supplier provides
   - Finds all products using those components
   - Finds all orders with those products
   - Calculates impact metrics

**Metrics Calculated:**
- Number of impacted orders
- Total revenue impact ($)
- Affected regions (list)
- Affected products (list)
- Affected dealers (list)
- Delayed orders count
- Orders breakdown by status
- Average order value

**Example:**
```
Supplier: S-123
↓ Supplies: COMP-0001, COMP-0045, COMP-0089
↓ Used in: PROD-3500, PROD-3600
↓ Impacted Orders: 47
↓ Impacted Revenue: $112.5M
↓ Affected Regions: North America, Europe, Asia Pacific
↓ Delayed Orders: 12
```

**Visual Display:**
- Metrics cards (large numbers)
- Status distribution chart
- Complete order listing
- Cypher query example

---

### 8. **Vector Search / AI Knowledge Retrieval**

**Advanced Feature: Semantic Search**

**Capabilities:**
- Natural language question input
- Semantic similarity matching
- Multi-document search
- Confidence scoring
- Evidence extraction
- Root cause generation

**Example Workflow:**
```
User Question:
"Why is order SO-1000456 delayed?"

AI Process:
1. Encode question with SentenceTransformers
2. Compare with document embeddings
3. Find most similar documents
4. Extract relevant excerpts
5. Generate explanation
6. Score confidence

Result:
Root Cause: "Turbocharger shortage from Supplier S-123"
Supporting Doc 1: supplier_bulletin.txt (0.87 relevance)
Supporting Doc 2: quality_alert.txt (0.82 relevance)
Supporting Doc 3: engineering_note.txt (0.79 relevance)
Confidence: 85%
```

**Technology:**
- Model: SentenceTransformers all-MiniLM-L6-v2
- Embeddings: 384-dimensional vectors
- Similarity: Cosine distance
- Storage: In-memory (fast)

---

### 9. **Professional UI/UX**

####  Branding
- Black (#000000) primary color
- Yellow (#FFCC00) accent color
- White backgrounds
- Professional fonts

#### Layout Features
- Responsive columns
- Expandable sections
- Clean dividers
- Organized tabs
- Clear hierarchy

#### Interactive Elements
- Dropdown selectors
- Buttons with emojis
- Expanding cards
- JSON viewers
- Plotly charts

#### Accessibility
- Clear labels
- Descriptive text
- Keyboard navigation
- Mobile responsive
- High contrast

---

### 10. **Executive Presentation Ready**

Features designed for presentations:

**Visual Elements:**
- Title and subtitle at top
- Executive summary with KPIs
- Clear three-column layout
- Professional color scheme
- Large, readable fonts

**Guided Experience:**
- Business questions dropdown
- Automatic model routing
- Explanation of why each model
- Personas identified
- Real data examples

**Demo Mode:**
- Guided tour button
- Step-by-step navigation
- Progress tracking
- Professional flow

**Documentation:**
- Clear labels everywhere
- Purpose statements
- Use case explanations
- Consumer personas
- Sample queries

---

### 11. **Performance Optimizations**

**Caching:**
- Data loaded once (`@st.cache_resource`)
- Graph built once
- Vector embeddings cached
- Results stored

**Lazy Loading:**
- Graphs only computed when tab accessed
- Vector model loaded on first search
- Charts rendered on-demand

**Efficiency:**
- CSV parsing is fast
- In-memory operations
- No external API calls
- Local computation

---

### 12. **Customization Points**

**Easy to Customize:**

1. **Business Questions** (`utils/routing.py`)
   - Add new questions
   - Change models
   - Update personas
   - Modify explanations

2. **Synthetic Data** (`generate_simple_data.py`)
   - Change order count
   - Modify product list
   - Adjust supplier network
   - Add custom fields

3. **Colors** (`.streamlit/config.toml`)
   - Primary color
   - Background color
   - Text color
   - Font selection

4. **Knowledge Documents** (`data/documents/`)
   - Add new documents
   - Update content
   - Customize alerts

---

## Advanced Features

### Machine Learning Ready
- Vector embeddings for ML
- Relationship data for GNNs
- Historical tracking possible
- Feature engineering support

### Scalability Path
- CSVs → SQL databases
- Local vectors → Pinecone/Weaviate
- NetworkX → Neo4j
- Streamlit → FastAPI backend

### Enterprise Features Ready
- Multi-tenant architecture possible
- Authentication hooks available
- Audit logging ready
- Monitoring integrations

---

## Security Features

**Demo Edition Includes:**
- Synthetic data only
- No authentication required
- Local-only operation
- No external dependencies
- No data exfiltration

**Production Ready Path:**
- Environment variables for secrets
- User authentication support
- Role-based access control
- Audit logging hooks
- Data encryption ready

---

## Performance Characteristics

| Operation | Time | Notes |
|-----------|------|-------|
| Load data | <1s | Cached after first load |
| Render dashboard | <2s | Plotly chart rendering |
| Graph traversal | <100ms | For supplier impact |
| Vector search | 200-500ms | First search, model download |
| Vector search (cached) | <50ms | Subsequent searches |
| JSON display | <100ms | Rendering |
| Table sorting | Instant | Interactive |

---

## Browser Compatibility

**Tested On:**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

**Requirements:**
- JavaScript enabled
- Cookies enabled
- 512MB RAM minimum
- 50MB disk (for models)

---

## Deployment Features

Includes configuration for:
- Local development
- Docker containerization
- Streamlit Cloud
- AWS EC2
- Heroku
- Google Cloud Run
- Azure Container Instances
- Kubernetes ready

---

## Documentation

Comprehensive guides included:
- **README.md** - Full technical documentation
- **QUICKSTART.md** - 5-minute setup
- **DEPLOYMENT.md** - 6 deployment options
- **FEATURES.md** - This file
- **Code comments** - Inline documentation

---

## Support & Extensibility

**Built-In Support For:**
- Custom business questions
- Additional data sources
- New data models
- Custom visualizations
- Extended knowledge base

**Easy to Add:**
- New Streamlit pages
- Custom charts
- Additional tables
- More suppliers/products
- More knowledge documents

---

**Prism Multi-Model Framework Demonstrator**

*Production-Quality | Feature-Rich | Executive-Ready*

Version 1.0.0 | Last Updated: 2026-07-12
