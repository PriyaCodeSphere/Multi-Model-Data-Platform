#!/usr/bin/env python3
"""
Synthetic Data Generation Script for Prism Demonstrator

Run this script to generate synthetic data:
    python generate_data.py
"""

from utils.data_generator import SyntheticDataGenerator
import os

if __name__ == "__main__":
    print("🏭 Prism Multi-Model Framework - Data Generation")
    print("=" * 50)
    
    # Create data directory
    os.makedirs("data/documents", exist_ok=True)
    
    # Generate data
    print("\n📊 Generating synthetic data...")
    generator = SyntheticDataGenerator(num_orders=1000, seed=42)
    data = generator.generate_all_data("data")
    
    print(f"✅ Generated {len(data['orders'])} sales orders")
    print(f"✅ Generated {len(data['suppliers'])} suppliers")
    print(f"✅ Generated {len(data['products'])} products")
    print(f"✅ Generated {len(data['graph_edges'])} graph relationships")
    print(f"✅ Generated 4 knowledge documents")
    
    print("\n📁 Data files created:")
    print("  • data/sales_orders.csv")
    print("  • data/suppliers.csv")
    print("  • data/products.csv")
    print("  • data/graph_edges.csv")
    print("  • data/documents/*.txt")
    
    print("\n✨ Data generation complete!")
    print("\n🚀 To run the Streamlit app:")
    print("  streamlit run app.py")
