"""
Graph Building and Visualization Utilities
"""

import networkx as nx
import pandas as pd
import numpy as np

class SupplierImpactGraph:
    def __init__(self, graph_edges_df, products_df, suppliers_df, orders_df):
        self.edges_df = graph_edges_df
        self.products_df = products_df
        self.suppliers_df = suppliers_df
        self.orders_df = orders_df
        self.G = None
        self.supplier_components: dict[str, list[str]] = {}
        self._build_graph()

    def _build_graph(self):
        """Build directed graph from edges."""
        self.G = nx.from_pandas_edgelist(
            self.edges_df,
            source="source",
            target="target",
            edge_attr="relationship",
            create_using=nx.DiGraph,
        )

        supplies_edges = self.edges_df[self.edges_df["relationship"] == "supplies"]
        self.supplier_components = (
            supplies_edges.groupby("source")["target"].apply(list).to_dict()
        )

    def get_suppliers_for_order(self, order_id: str) -> list[tuple[str, int]]:
        """Return suppliers involved in an order, ranked by component count.

        Traces order -> product -> components -> suppliers via the edge table.
        Each tuple is (supplier_id, num_components_this_supplier_provides).
        """
        order_row = self.orders_df[self.orders_df["order_id"] == order_id]
        if order_row.empty:
            return []
        product_id = order_row.iloc[0]["product_id"]

        components = self.edges_df[
            (self.edges_df["target"] == product_id)
            & (self.edges_df["relationship"] == "belongs_to")
        ]["source"].tolist()
        if not components:
            return []

        supplier_counts = (
            self.edges_df[
                (self.edges_df["target"].isin(components))
                & (self.edges_df["relationship"] == "supplies")
            ]["source"]
            .value_counts()
        )
        return list(supplier_counts.items())

    def find_impacted_orders(self, supplier_id):
        """Find all orders impacted by a supplier issue"""
        if supplier_id not in self.G:
            return []
        
        impacted_orders = set()
        
        # BFS from supplier to find all reachable orders
        queue = [supplier_id]
        visited = set()
        
        while queue:
            node = queue.pop(0)
            if node in visited:
                continue
            visited.add(node)
            
            # Check if this is an order
            if node.startswith('SO-'):
                impacted_orders.add(node)
            
            # Traverse edges
            if node in self.G:
                for neighbor in self.G.successors(node):
                    if neighbor not in visited:
                        queue.append(neighbor)
        
        return list(impacted_orders)
    
    def get_impact_path(self, supplier_id, target_order=None):
        """Get path from supplier to order showing impact chain"""
        if supplier_id not in self.G:
            return None
        
        paths = []
        
        # Find all paths from supplier to orders
        for node in self.G.nodes():
            if node.startswith('SO-'):
                try:
                    path = nx.shortest_path(self.G, supplier_id, node)
                    paths.append(path)
                    if target_order and node == target_order:
                        return path
                except nx.NetworkXNoPath:
                    continue
        
        # Return first path found
        return paths[0] if paths else None
    
    def get_impact_analytics(self, supplier_id):
        """Get impact analytics for supplier disruption"""
        impacted_orders = self.find_impacted_orders(supplier_id)
        
        # Merge with order data
        impacted_order_details = self.orders_df[
            self.orders_df['order_id'].isin(impacted_orders)
        ].copy()
        
        analytics = {
            "supplier_id": supplier_id,
            "total_impacted_orders": len(impacted_order_details),
            "total_impacted_amount": impacted_order_details['amount'].sum(),
            "impacted_regions": impacted_order_details['region'].unique().tolist(),
            "impacted_products": impacted_order_details['product_id'].unique().tolist(),
            "impacted_customers": impacted_order_details['customer_id'].unique().tolist(),
            "delayed_orders": len(impacted_order_details[
                impacted_order_details['status'].isin(['On Hold', 'Back Ordered', 'Cancelled'])
            ]),
            "orders_by_status": impacted_order_details['status'].value_counts().to_dict(),
        }
        
        if len(impacted_order_details) > 0:
            analytics["avg_order_amount"] = impacted_order_details['amount'].mean()
            analytics["max_order_amount"] = impacted_order_details['amount'].max()
        
        return analytics, impacted_order_details
    
    def build_visualization_graph(self, supplier_id, max_depth=4):
        """Build subgraph for visualization"""
        # Start from supplier and traverse graph
        subgraph_nodes = set([supplier_id])
        queue = [(supplier_id, 0)]
        
        while queue:
            node, depth = queue.pop(0)
            if depth >= max_depth:
                continue
            
            if node in self.G:
                for successor in self.G.successors(node):
                    if successor not in subgraph_nodes:
                        subgraph_nodes.add(successor)
                        queue.append((successor, depth + 1))
        
        # Create subgraph
        subgraph = self.G.subgraph(subgraph_nodes).copy()
        
        return subgraph
    
    def get_node_colors(self, graph):
        """Get node colors for visualization"""
        colors = {}
        for node in graph.nodes():
            if node.startswith('Supplier'):
                colors[node] = '#D4A017'  # Gold for suppliers
            elif node.startswith('COMP'):
                colors[node] = '#808080'  # Gray for components
            elif node.startswith('CAT'):
                colors[node] = '#000000'  # Black for products
            elif node.startswith('SO-'):
                colors[node] = '#DC0000'  # Red for orders
            elif node.startswith('Dealer'):
                colors[node] = '#0047AB'  # Blue for dealers
            else:
                colors[node] = '#CCCCCC'  # Light gray default
        return colors
    
    def get_node_sizes(self, graph):
        """Get node sizes for visualization"""
        sizes = {}
        for node in graph.nodes():
            if node.startswith('Supplier'):
                sizes[node] = 3000  # Large for suppliers
            elif node.startswith('SO-'):
                sizes[node] = 2000  # Large for orders
            else:
                sizes[node] = 1500
        return sizes
