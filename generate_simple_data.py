"""
Standalone Data Generator - No External Dependencies
Generates synthetic sales order data using only Python standard library
"""

import csv
import os
import random
from datetime import datetime, timedelta
import json

class SimpleDataGenerator:
    def __init__(self, num_orders=1000, seed=42):
        self.num_orders = num_orders
        random.seed(seed)
        
        # Master data
        self.regions = ["North America", "South America", "Europe", "Asia Pacific", "Africa"]
        self.suppliers = [f"Supplier-S{i:03d}" for i in range(1, 21)]
        self.dealers = [f"Dealer-D{i:03d}" for i in range(1, 51)]
        self.products = [
            ("PROD-3500", "Model 3500 Engine", "Engines"),
            ("PROD-3600", "Model 3600 Engine", "Engines"),
            ("PROD-380", "Model 380F Excavator", "Excavators"),
            ("PROD-390", "Model 390F Excavator", "Excavators"),
            ("PROD-320", "Model 320 Excavator", "Excavators"),
            ("PROD-950", "Model 950 Wheel Loader", "Loaders"),
            ("PROD-980", "Model 980 Wheel Loader", "Loaders"),
            ("PROD-D10", "Model D10 Bulldozer", "Dozers"),
            ("PROD-D9", "Model D9 Bulldozer", "Dozers"),
            ("PROD-D6", "Model D6 Bulldozer", "Dozers"),
        ]
        self.components = [f"COMP-{i:04d}" for i in range(1, 101)]
        self.statuses = [
            "Draft", "Submitted", "Booked", "Scheduled", "In Production",
            "Shipped", "Delivered", "Invoiced", "On Hold", "Back Ordered",
        ]
        self.quarters = ["Q1-2026", "Q2-2026", "Q3-2026", "Q4-2026"]
        
        # Supplier-Component mapping
        self.supplier_components = {}
        for supplier in self.suppliers:
            num_components = random.randint(3, 8)
            self.supplier_components[supplier] = random.sample(
                self.components, num_components
            )
        
        # Component-Product mapping
        self.product_components = {}
        for product_id, _, _ in self.products:
            num_components = random.randint(5, 15)
            self.product_components[product_id] = random.sample(
                self.components, num_components
            )
    
    def generate_sales_orders(self):
        """Generate sales orders"""
        orders = []
        base_date = datetime(2026, 1, 1)
        
        for i in range(self.num_orders):
            order_id = f"SO-{1000000 + i}"
            dealer_id = random.choice(self.dealers)
            product_id, product_name, product_family = random.choice(self.products)
            
            # Random date
            days_offset = random.randint(0, 180)
            order_date = base_date + timedelta(days=days_offset)
            
            # Quantities and pricing
            quantity = random.choice([1, 2, 3, 4, 5, 6, 8, 10, 12])
            unit_price = random.uniform(50000, 500000)
            amount = quantity * unit_price
            
            # Status distribution
            status_weights = [0.05, 0.08, 0.10, 0.10, 0.15, 0.15, 0.20, 0.07, 0.05, 0.05]
            status = random.choices(self.statuses, weights=status_weights)[0]
            
            orders.append({
                "order_id": order_id,
                "customer_id": dealer_id,
                "product_id": product_id,
                "product_name": product_name,
                "product_family": product_family,
                "order_date": order_date.strftime("%Y-%m-%d"),
                "status": status,
                "quantity": quantity,
                "unit_price": f"{unit_price:.2f}",
                "amount": f"{amount:.2f}",
                "region": random.choice(self.regions),
                "forecast_quarter": random.choice(self.quarters),
                "notes": "Sample order note"
            })
        
        return orders
    
    def generate_suppliers(self):
        """Generate supplier data"""
        suppliers = []
        countries = ["USA", "Germany", "Japan", "Brazil", "China"]
        
        for supplier_id in self.suppliers:
            suppliers.append({
                "supplier_id": supplier_id,
                "supplier_name": f"Manufacturing Company {supplier_id}",
                "country": random.choice(countries),
                "quality_score": f"{random.uniform(0.85, 0.99):.2f}",
                "on_time_delivery_pct": f"{random.uniform(0.88, 0.98):.2f}",
                "status": random.choice(["Active", "Active", "Active", "At Risk", "Probation"]),
            })
        
        return suppliers
    
    def generate_products(self):
        """Generate product data"""
        products = []
        
        for product_id, product_name, product_family in self.products:
            products.append({
                "id": product_id,
                "name": product_name,
                "family": product_family,
                "unit_cost": f"{random.uniform(40000, 450000):.2f}",
                "lead_time_days": random.randint(14, 120),
                "availability_pct": f"{random.uniform(0.80, 0.99):.2f}"
            })
        
        return products
    
    def generate_graph_edges(self, orders):
        """Generate graph relationships"""
        edges = []
        
        # Supplier -> Component
        for supplier_id, components in self.supplier_components.items():
            for component_id in components:
                edges.append({
                    "source": supplier_id,
                    "target": component_id,
                    "relationship": "supplies"
                })
        
        # Component -> Product
        for product_id, components in self.product_components.items():
            for component_id in components:
                edges.append({
                    "source": component_id,
                    "target": product_id,
                    "relationship": "belongs_to"
                })
        
        # Product -> Order -> Customer
        for order in orders:
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
        
        return edges
    
    def save_to_csv(self, data, filename):
        """Save data to CSV"""
        if not data:
            return
        
        keys = data[0].keys()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
    
    def generate_all_data(self, output_dir="data"):
        """Generate all data and save to CSV"""
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(f"{output_dir}/documents", exist_ok=True)
        
        print("📊 Generating sales orders...")
        orders = self.generate_sales_orders()
        self.save_to_csv(orders, f"{output_dir}/sales_orders.csv")
        print(f"   ✅ Created {len(orders)} sales orders")
        
        print("📊 Generating suppliers...")
        suppliers = self.generate_suppliers()
        self.save_to_csv(suppliers, f"{output_dir}/suppliers.csv")
        print(f"   ✅ Created {len(suppliers)} suppliers")
        
        print("📊 Generating products...")
        products = self.generate_products()
        self.save_to_csv(products, f"{output_dir}/products.csv")
        print(f"   ✅ Created {len(products)} products")
        
        print("📊 Generating graph relationships...")
        edges = self.generate_graph_edges(orders)
        self.save_to_csv(edges, f"{output_dir}/graph_edges.csv")
        print(f"   ✅ Created {len(edges)} relationships")
        
        print("📊 Generating knowledge documents...")
        self._generate_documents(output_dir)
        print("   ✅ Created 4 knowledge documents")
        
        return {
            "orders": len(orders),
            "suppliers": len(suppliers),
            "products": len(products),
            "edges": len(edges)
        }
    
    def _generate_documents(self, output_dir):
        """Generate knowledge documents"""
        docs = {
            "supplier_bulletin.txt": """SUPPLIER QUALITY BULLETIN - July 2026

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
Status: ACTIVE""",

            "engineering_note.txt": """ENGINEERING MEMO - Q4 2026 Production Planning

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

Technical Contact: engineering-supply@example.com""",

            "service_manual.txt": """SERVICE MANUAL - Engine Systems

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
Suppliers scoring below 90% on on-time delivery represent risk.""",

            "quality_alert.txt": """QUALITY ALERT - Q3 2026

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
Estimated Resolution: August 30, 2026"""
        }
        
        for filename, content in docs.items():
            filepath = os.path.join(output_dir, "documents", filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)


if __name__ == "__main__":
    print("🏭 Prism Multi-Model Framework - Data Generation")
    print("=" * 50)
    print()
    
    generator = SimpleDataGenerator(num_orders=1000, seed=42)
    stats = generator.generate_all_data("data")
    
    print()
    print("✨ Data generation complete!")
    print()
    print("📁 Files created:")
    print("  • data/sales_orders.csv")
    print("  • data/suppliers.csv")
    print("  • data/products.csv")
    print("  • data/graph_edges.csv")
    print("  • data/documents/*.txt")
    print()
    print("🎯 Summary:")
    for key, value in stats.items():
        print(f"  • {key.replace('_', ' ').title()}: {value:,}")
    print()
    print("📝 NOTE: Install dependencies with: pip install -r requirements.txt")
    print("🚀 Then run the app with: streamlit run app.py")
