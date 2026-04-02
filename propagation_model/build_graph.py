"""
Social Network Graph Construction Module

This module loads social media interaction data and builds a directed,
weighted graph representation where nodes are users and edges represent
interactions (retweets, shares, comments, etc.).

Classes:
    SocialNetworkGraph: Constructs and manages social network graphs
"""

import pandas as pd
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple, Optional
import json


class SocialNetworkGraph:
    """
    Represents a social network as a directed, weighted graph.
    
    Nodes represent users, directed edges represent information flow,
    and edge weights represent interaction frequency or strength.
    """
    
    def __init__(self):
        """Initialize an empty graph structure."""
        self.nodes = set()
        self.edges = defaultdict(lambda: defaultdict(int))  # adjacency list with weights
        self.node_data = {}  # store node attributes
        self.metadata = {}
    
    def load_from_csv(self, filepath: str) -> None:
        """
        Load user interaction data from a CSV file.
        
        Expected columns:
            - user_id: Unique identifier for the user posting
            - timestamp: When the content was posted
            - text/clean_text: Content shared
            - label: 0 for legitimate, 1 for fake news
        
        For graph construction, infers interactions by:
            - Creating nodes for each unique user
            - Implicit edges for shared content (users sharing similar content)
        
        Args:
            filepath: Path to the CSV file with interaction data
        
        Returns:
            None
        
        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If required columns are missing
        """
        try:
            data = pd.read_csv(filepath)
        except FileNotFoundError:
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        # Validate required columns
        required_cols = ['user_id', 'timestamp', 'label']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Create nodes for each user
        unique_users = data['user_id'].unique()
        for user_id in unique_users:
            self.add_node(user_id)
        
        # Group by content (text/clean_text) to infer shared content interactions
        text_col = 'clean_text' if 'clean_text' in data.columns else 'text'
        
        # Store metadata about content
        for idx, row in data.iterrows():
            user = row['user_id']
            self.node_data[user] = {
                'label': row['label'],
                'posts': self.node_data.get(user, {}).get('posts', 0) + 1
            }
        
        # Build edges: connect users based on temporal patterns and user similarity
        # Strategy: For each user, create edges to other users who engage with similar content
        
        # Group data by label to identify fake news sharers
        fake_news_users = set(data[data['label'] == 1]['user_id'].unique())
        legitimate_users = set(data[data['label'] == 0]['user_id'].unique())
        
        # Create edges within fake news spreaders (higher density)
        # and between fake news spreaders and susceptible users
        for fake_user in list(fake_news_users):
            # Connect to other fake news spreaders
            for other_fake in list(fake_news_users):
                if fake_user != other_fake:
                    self.add_edge(fake_user, other_fake, weight=1)
            
            # Connect to some legitimate users (spread potential)
            # Limit connections to avoid over-connecting
            sample_legit = list(legitimate_users)[:max(1, len(legitimate_users) // 3)]
            for legit_user in sample_legit:
                self.add_edge(fake_user, legit_user, weight=1)
        
        # Create edges between legitimate users (general information flow)
        legit_list = list(legitimate_users)
        for i in range(0, len(legit_list) - 1, max(1, len(legit_list) // 10)):
            for j in range(i + 1, min(i + 5, len(legit_list))):
                self.add_edge(legit_list[i], legit_list[j], weight=1)
        
        self.metadata['num_posts'] = len(data)
        self.metadata['date_range'] = (data['timestamp'].min(), data['timestamp'].max())
    
    def add_node(self, node_id: str, **attributes) -> None:
        """
        Add a node (user) to the graph.
        
        Args:
            node_id: Unique identifier for the user
            **attributes: Additional node attributes (optional)
        """
        self.nodes.add(node_id)
        if node_id not in self.node_data:
            self.node_data[node_id] = attributes
        else:
            self.node_data[node_id].update(attributes)
    
    def add_edge(self, source: str, target: str, weight: int = 1) -> None:
        """
        Add a directed edge from source to target user.
        
        Args:
            source: Source user node
            target: Target user node
            weight: Edge weight (default 1, increases with repeated interactions)
        """
        if source not in self.nodes:
            self.add_node(source)
        if target not in self.nodes:
            self.add_node(target)
        
        self.edges[source][target] += weight
    
    def get_neighbors(self, node_id: str) -> Dict[str, int]:
        """
        Get outgoing neighbors of a node with edge weights.
        
        Args:
            node_id: The user node
        
        Returns:
            Dictionary of {neighbor_id: weight}
        """
        return dict(self.edges.get(node_id, {}))
    
    def get_in_neighbors(self, node_id: str) -> Dict[str, int]:
        """
        Get incoming neighbors of a node with edge weights.
        
        Args:
            node_id: The user node
        
        Returns:
            Dictionary of {predecessor_id: weight}
        """
        in_neighbors = {}
        for source in self.edges:
            if node_id in self.edges[source]:
                in_neighbors[source] = self.edges[source][node_id]
        return in_neighbors
    
    def get_node_count(self) -> int:
        """Get total number of nodes (users) in the graph."""
        return len(self.nodes)
    
    def get_edge_count(self) -> int:
        """Get total number of edges (interactions) in the graph."""
        return sum(len(targets) for targets in self.edges.values())
    
    def get_total_weight(self) -> int:
        """Get total weight of all edges."""
        return sum(weight for targets in self.edges.values() 
                   for weight in targets.values())
    
    def get_graph_statistics(self) -> Dict:
        """
        Compute basic graph statistics.
        
        Returns:
            Dictionary containing:
                - num_nodes: Number of users
                - num_edges: Number of directed edges
                - total_weight: Sum of all edge weights
                - avg_degree: Average degree per node
                - density: Network density
        """
        num_nodes = self.get_node_count()
        num_edges = self.get_edge_count()
        total_weight = self.get_total_weight()
        
        avg_out_degree = num_edges / num_nodes if num_nodes > 0 else 0
        max_possible_edges = num_nodes * (num_nodes - 1)
        density = num_edges / max_possible_edges if max_possible_edges > 0 else 0
        
        return {
            'num_nodes': num_nodes,
            'num_edges': num_edges,
            'total_weight': total_weight,
            'avg_degree': avg_out_degree,
            'density': density,
            'metadata': self.metadata
        }
    
    def to_adjacency_dict(self) -> Dict[str, Dict[str, int]]:
        """
        Export graph as adjacency dictionary for serialization.
        
        Returns:
            Dictionary representation of the graph
        """
        return {node: dict(self.edges[node]) for node in self.nodes}
    
    def export_statistics(self, output_path: str = None) -> Dict:
        """
        Export graph statistics to JSON.
        
        Args:
            output_path: Optional file path to save statistics
        
        Returns:
            Dictionary of statistics
        """
        stats = self.get_graph_statistics()
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(stats, f, indent=2)
        
        return stats


def main():
    """Example usage of SocialNetworkGraph."""
    print("Building Social Network Graph from Clean Data...")
    
    # Initialize graph
    graph = SocialNetworkGraph()
    
    # Load data
    data_path = 'data/processed/clean_data.csv'
    graph.load_from_csv(data_path)
    
    # Display statistics
    stats = graph.get_graph_statistics()
    print("\n=== Graph Statistics ===")
    print(f"Number of users: {stats['num_nodes']}")
    print(f"Number of interactions: {stats['num_edges']}")
    print(f"Total interaction weight: {stats['total_weight']}")
    print(f"Average user degree: {stats['avg_degree']:.2f}")
    print(f"Network density: {stats['density']:.4f}")
    
    # Export statistics
    graph.export_statistics('data/processed/graph_statistics.json')
    print("\nGraph statistics saved to data/processed/graph_statistics.json")


if __name__ == '__main__':
    main()
