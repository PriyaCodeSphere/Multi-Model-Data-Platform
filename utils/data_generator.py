"""
Data Generation Utilities for Prism Multi-Model Framework Demonstrator
Generates realistic synthetic sales order data
"""

import pandas as pd
import numpy as np
from faker import Faker
from datetime import datetime, timedelta
import json
import os

fake = Faker()
np.random.seed(42)
Faker.seed(42)

class SyntheticDataGenerator:
    def __init__(self, num_orders=1000, seed=42):
        self.num_orders = num_orders
        self.seed = seed
        np.random.seed(seed)
        Faker.seed(seed)
        
        # Define master data
        self.regions = ["North America", "South America", "Europe", "Asia Pacific", "Africa"]
        self.suppliers = [f"Supplier-S{i:03d}" for i in range(1, 21)]
        self.dealers = [f"Dealer-D{i:03d}" for i in range(1, 51)]
        self.products = [
            {"id": f"PROD-3500", "name": "Model 3500 Engine", "family": "Engines"},
            {"id": f"PROD-3600", "name": "Model 3600 Engine", "family": "Engines"},
            {"id": f"PROD-380", "name": "Model 380F Excavator", "family": "Excavators"},
            {"id": f"PROD-390", "name": "Model 390F Excavator", "family": "Excavators"},
            {"id": f"PROD-320", "name": "Model 320 Excavator", "family": "Excavators"},
            {"id": f"PROD-950", "name": "Model 950 Wheel Loader", "family": "Loaders"},
            {"id": f"PROD-980", "name": "Model 980 Wheel Loader", "family": "Loaders"},
            {"id": f"PROD-D10", "name": "Model D10 Bulldozer", "family": "Dozers"},
            {"id": f"PROD-D9", "name": "Model D9 Bulldozer", "family": "Dozers"},
            {"id": f"PROD-D6", "name": "Model D6 Bulldozer", "family": "Dozers"},
        ]
        self.components = [f"COMP-{i:04d}" for i in range(1, 101)]
        self.statuses = ["Confirmed", "In Production", "Shipped", "Delivered", "Delayed", "Backlog"]
        self.quarters = ["Q1-2026", "Q2-2026", "Q3-2026", "Q4-2026"]
        
        # Supplier-Component mapping
        self.supplier_components = {}
        for supplier in self.suppliers:
            num_components = np.random.randint(3, 8)
            self.supplier_components[supplier] = np.random.choice(
                self.components, num_components, replace=False
            ).tolist()
        
        # Component-Product mapping
        self.product_components = {}
        for product in self.products:
            num_components = np.random.randint(5, 15)
            self.product_components[product["id"]] = np.random.choice(
                self.components, num_components, replace=False
            ).tolist()
    
    def generate_sales_orders(self):
        """Generate Sales Order Header data"""
        orders = []
        base_date = datetime(2026, 1, 1)
        
        for i in range(self.num_orders):
            order_id = f"SO-{1000000 + i}"
            dealer_id = np.random.choice(self.dealers)
            product = np.random.choice(self.products)
            
            # Realistic order date distribution
            days_offset = np.random.randint(0, 180)
            order_date = base_date + timedelta(days=days_offset)
            
            # Quantities
            quantity = np.random.choice([1, 2, 3, 4, 5, 6, 8, 10, 12])
            unit_price = np.random.uniform(50000, 500000)
            amount = quantity * unit_price
            
            # Status distribution
            status_weights = [0.15, 0.20, 0.15, 0.25, 0.15, 0.10]  # Delayed included
            status = np.random.choice(self.statuses, p=status_weights)
            
            orders.append({
                "order_id": order_id,
                "customer_id": dealer_id,
                "product_id": product["id"],
                "product_name": product["name"],
                "product_family": product["family"],
                "order_date": order_date,
                "status": status,
                "quantity": quantity,
                "unit_price": unit_price,
                "amount": amount,
                "region": np.random.choice(self.regions),
                "forecast_quarter": np.random.choice(self.quarters),
                "notes": fake.sentence(nb_words=8),
            })
        
        return pd.DataFrame(orders)
    
    def generate_suppliers(self):
        """Generate Supplier data"""
        suppliers = []
        for supplier_id in self.suppliers:
            suppliers.append({
                "supplier_id": supplier_id,
                "supplier_name": f"{fake.company()} Manufacturing",
                "country": np.random.choice(["USA", "Germany", "Japan", "Brazil", "China"]),
                "quality_score": np.random.uniform(0.85, 0.99),
                "on_time_delivery_pct": np.random.uniform(0.88, 0.98),
                "status": np.random.choice(["Active", "Active", "Active", "At Risk", "Probation"]),
            })
        return pd.DataFrame(suppliers)
    
    def generate_products(self):
        """Generate Product data"""
        return pd.DataFrame(self.products).assign(
            unit_cost=lambda x: np.random.uniform(40000, 450000, len(x)),
            lead_time_days=lambda x: np.random.randint(14, 120, len(x)),
            availability_pct=lambda x: np.random.uniform(0.80, 0.99, len(x))
        )
    
    def generate_graph_edges(self, orders_df=None):
        """Generate graph relationships.

        Accepts a pre-generated orders DataFrame so the caller can guarantee
        the edges reference the same order rows that are persisted to CSV.
        """
        if orders_df is None:
            orders_df = self.generate_sales_orders()

        edges = []
        
        # Supplier -> Component relationships
        for supplier_id, components in self.supplier_components.items():
            for component_id in components:
                edges.append({
                    "source": supplier_id,
                    "target": component_id,
                    "relationship": "supplies"
                })
        
        # Component -> Product relationships
        for product_id, components in self.product_components.items():
            for component_id in components:
                edges.append({
                    "source": component_id,
                    "target": product_id,
                    "relationship": "belongs_to"
                })
        
        # Product -> Order relationships
        for _, order in orders_df.iterrows():
            edges.append({
                "source": order["product_id"],
                "target": order["order_id"],
                "relationship": "linked_to"
            })
            edges.append({
                "source": order["order_id"],
                "target": order["customer_id"],
                "relationship": "ordered_by"
            })
        
        return pd.DataFrame(edges)
    
    def generate_all_data(self, output_dir="data"):
        """Generate all synthetic data and save to CSV"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate all datasets. Orders are generated first and reused so the
        # graph edges reference the exact rows written to sales_orders.csv.
        orders = self.generate_sales_orders()
        suppliers = self.generate_suppliers()
        products = self.generate_products()
        graph_edges = self.generate_graph_edges(orders_df=orders)
        
        # Save to CSV
        orders.to_csv(f"{output_dir}/sales_orders.csv", index=False)
        suppliers.to_csv(f"{output_dir}/suppliers.csv", index=False)
        products.to_csv(f"{output_dir}/products.csv", index=False)
        graph_edges.to_csv(f"{output_dir}/graph_edges.csv", index=False)
        
        # Generate knowledge documents
        self._generate_knowledge_documents(output_dir, orders, suppliers)
        
        return {
            "orders": orders,
            "suppliers": suppliers,
            "products": products,
            "graph_edges": graph_edges
        }
    
    def _generate_knowledge_documents(self, output_dir, orders, suppliers):
        """Generate mock knowledge documents for vector search"""
        docs_dir = f"{output_dir}/documents"
        os.makedirs(docs_dir, exist_ok=True)
        
        # Supplier Bulletin
        supplier_bulletin = """SUPPLIER QUALITY BULLETIN - July 2026

ALERT: Turbocharger Shortage from Supplier S-123

Effective immediately, Supplier S-123 has reported critical production delays
on turbocharger components due to semiconductor chip shortage.

Impact: All turbocharger variants including advanced and standard models
are affected with 8-12 week lead time extensions.

Affected Products:
- Model 3500 Engine (advanced cooling systems)
- Model 3600 Engine (heavy-duty variants)

Recommended Actions:
1. Adjust demand forecasts for Q3-Q4 2026
2. Consider alternative suppliers for non-critical applications
3. Expedite orders before August 15 cutoff

Escalation Contact: supplier-ops@example.com
Status: ACTIVE
"""
        
        # Engineering Note
        engineering_note = """ENGINEERING MEMO - Q4 2026 Production Planning

Subject: Component Sourcing Constraints

This memo outlines critical component sourcing issues affecting
2026 production schedules.

Issue 1: Turbocharger Supply Chain Disruption
- Supplier S-123 experienced facility shutdown in July
- Alternative suppliers have limited capacity
- Estimated recovery: Q4 2026
- Affected engine families: 3500, 3600

Issue 2: Advanced Cooling System Availability
- Heavy-duty cooling systems in high demand
- Lead times extended from 6 to 12 weeks
- Recommend customer communication on delivery dates

Mitigation Strategy:
- Activate secondary suppliers for turbocharger assemblies
- Increase buffer stock for cooling systems
- Implement demand smoothing across quarters

Technical Contact: engineering-supply@example.com
"""
        
        # Service Manual
        service_manual = """SERVICE MANUAL - Engine Systems

Chapter 3: Troubleshooting Common Delays

3.1 Turbocharger Issues
Turbochargers are critical for engine performance. Common sources of
production delays include:

- Supply chain disruptions from primary suppliers
- Quality inspection failures requiring rework
- Integration compatibility issues with cooling systems
- Certification delays for new turbocharger variants

Delayed deliveries often correlate with turbocharger availability.
Root cause analysis should verify component source.

3.2 Cooling System Integration
Heavy-duty cooling systems require extended integration testing.
Quality gates may add 2-3 weeks to production schedules.

3.3 Supply Chain Risk
Monitor supplier quality scores and on-time delivery metrics.
Suppliers scoring below 90% on on-time delivery represent risk.
"""
        
        # Quality Alert
        quality_alert = """QUALITY ALERT - Q3 2026

Alert ID: QA-2026-0847
Date: July 15, 2026

Subject: Turbocharger Defect Analysis

A quality inspection at Supplier S-123 identified potential defects
in turbocharger manufacturing processes affecting production batches
from June-July 2026.

Defect Type: Bearing clearance out of specification
Severity: Medium
Scope: Estimated 400+ units affected

Products Impacted:
- CAT 3500 engines with advanced turbocharger options
- Some CAT 3600 heavy-duty variants

Corrective Actions:
1. Full inspection of all affected components in inventory
2. Customer notification for affected orders
3. Production delay of 4-6 weeks for inspection and rework

Root Cause: Tooling calibration drift in manufacturing
Preventive Measures: Enhanced incoming inspection protocols

Status: IN PROGRESS
Estimated Resolution: August 30, 2026
"""
        
        # Write documents
        with open(f"{docs_dir}/supplier_bulletin.txt", "w") as f:
            f.write(supplier_bulletin)
        
        with open(f"{docs_dir}/engineering_note.txt", "w") as f:
            f.write(engineering_note)
        
        with open(f"{docs_dir}/service_manual.txt", "w") as f:
            f.write(service_manual)
        
        with open(f"{docs_dir}/quality_alert.txt", "w") as f:
            f.write(quality_alert)


def load_or_generate_data(data_dir="data"):
    """Load existing data or generate new data if not available"""
    if all(os.path.exists(f"{data_dir}/{f}") for f in 
           ["sales_orders.csv", "suppliers.csv", "products.csv", "graph_edges.csv"]):
        # Load existing data
        orders = pd.read_csv(f"{data_dir}/sales_orders.csv")
        orders["order_date"] = pd.to_datetime(orders["order_date"])
        suppliers = pd.read_csv(f"{data_dir}/suppliers.csv")
        products = pd.read_csv(f"{data_dir}/products.csv")
        graph_edges = pd.read_csv(f"{data_dir}/graph_edges.csv")
        
        return {
            "orders": orders,
            "suppliers": suppliers,
            "products": products,
            "graph_edges": graph_edges
        }
    else:
        # Generate new data
        generator = SyntheticDataGenerator(num_orders=1000)
        return generator.generate_all_data(data_dir)
