"""
Propagation Metrics Module

This module computes network centrality measures and influence metrics to
identify the most important spreaders in the social network.

Classes:
    PropagationMetrics: Computes various centrality and influence metrics
"""

import numpy as np
from typing import Dict, List, Tuple
from collections import deque
import json


class PropagationMetrics:
    """
    Compute centrality and influence metrics for social network nodes.
    
    Metrics:
        - Degree centrality: Number of direct connections
        - Betweenness centrality: Importance as bridge between communities
        - Closeness centrality: Average distance to other nodes
        - Eigenvector centrality: Influence based on influential connections
        - Spread potential: Expected spread if a node becomes infected
    """
    
    def __init__(self, graph):
        """
        Initialize metrics calculator.
        
        Args:
            graph: SocialNetworkGraph object
        """
        self.graph = graph
        self.metrics_cache = {}
    
    def degree_centrality(self) -> Dict[str, float]:
        """
        Compute degree centrality for all nodes.
        
        Degree centrality = out_degree / (n-1)
        where n is the number of nodes.
        
        Returns:
            Dictionary mapping node_id to centrality score (0-1)
        """
        n = self.graph.get_node_count()
        if n <= 1:
            return {node: 0.0 for node in self.graph.nodes}
        
        centrality = {}
        for node in self.graph.nodes:
            out_degree = len(self.graph.get_neighbors(node))
            centrality[node] = out_degree / (n - 1)
        
        return centrality
    
    def in_degree_centrality(self) -> Dict[str, float]:
        """
        Compute in-degree centrality for all nodes.
        
        In-degree centrality = in_degree / (n-1)
        
        Returns:
            Dictionary mapping node_id to in-centrality score (0-1)
        """
        n = self.graph.get_node_count()
        if n <= 1:
            return {node: 0.0 for node in self.graph.nodes}
        
        centrality = {}
        for node in self.graph.nodes:
            in_degree = len(self.graph.get_in_neighbors(node))
            centrality[node] = in_degree / (n - 1)
        
        return centrality
    
    def betweenness_centrality(self, sample_size: int = None) -> Dict[str, float]:
        """
        Compute betweenness centrality using shortest paths.
        
        Betweenness = sum of (shortest paths through node / total shortest paths)
        
        For large graphs, uses sampling to improve performance.
        
        Args:
            sample_size: Number of source-target pairs to sample (None=all pairs)
        
        Returns:
            Dictionary mapping node_id to betweenness score
        """
        nodes = list(self.graph.nodes)
        n = len(nodes)
        
        if n == 0:
            return {}
        
        # Initialize counters
        betweenness = {node: 0.0 for node in nodes}
        
        # If graph is large, sample pairs
        if sample_size is None:
            pairs = [(nodes[i], nodes[j]) for i in range(n) for j in range(i + 1, n)]
        else:
            sample_size = min(sample_size, len(nodes) * (len(nodes) - 1) // 2)
            pair_indices = np.random.choice(
                n * (n - 1) // 2, size=sample_size, replace=False
            )
            pairs = []
            for idx in pair_indices:
                i = idx // (n - 1)
                j = (idx % (n - 1)) + 1
                if j <= i:
                    j = i + 1 + (j - 1)
                pairs.append((nodes[i], nodes[j]))
        
        # For each pair, find shortest paths
        for source, target in pairs:
            paths = self._find_all_shortest_paths(source, target)
            
            if paths:
                for path in paths:
                    for node in path[1:-1]:  # Exclude source and target
                        betweenness[node] += 1.0 / len(paths)
        
        # Normalize
        if len(pairs) > 0:
            norm_factor = 2.0 / ((n - 1) * (n - 2))
            for node in betweenness:
                betweenness[node] *= norm_factor
        
        return betweenness
    
    def closeness_centrality(self) -> Dict[str, float]:
        """
        Compute closeness centrality based on average distance to other nodes.
        
        Closeness = (n-1) / sum of shortest distances
        
        Returns:
            Dictionary mapping node_id to closeness score (0-1)
        """
        nodes = list(self.graph.nodes)
        n = len(nodes)
        
        if n <= 1:
            return {node: 0.0 for node in nodes}
        
        closeness = {}
        
        for node in nodes:
            distances = self._bfs_distances(node)
            
            # Sum of distances to reachable nodes
            total_distance = sum(distances.values())
            
            # Average distance to reachable nodes
            reachable = len([d for d in distances.values() if d > 0])
            
            if reachable == 0:
                closeness[node] = 0.0
            else:
                avg_distance = total_distance / reachable if reachable > 0 else float('inf')
                closeness[node] = (reachable / (n - 1)) / (avg_distance if avg_distance > 0 else float('inf'))
        
        return closeness
    
    def eigenvector_centrality(self, iterations: int = 100, tolerance: float = 1e-6) -> Dict[str, float]:
        """
        Compute eigenvector centrality using power iteration.
        
        Eigenvector centrality measures influence based on connections
        to other influential nodes.
        
        Args:
            iterations: Number of power iteration steps
            tolerance: Convergence tolerance
        
        Returns:
            Dictionary mapping node_id to eigenvector centrality score
        """
        nodes = list(self.graph.nodes)
        n = len(nodes)
        
        if n == 0:
            return {}
        
        node_to_idx = {node: i for i, node in enumerate(nodes)}
        
        # Build adjacency matrix
        adj_matrix = np.zeros((n, n))
        for source in nodes:
            neighbors = self.graph.get_neighbors(source)
            for target, weight in neighbors.items():
                i, j = node_to_idx[source], node_to_idx[target]
                adj_matrix[i][j] = weight
        
        # Power iteration
        x = np.ones(n) / n
        
        for _ in range(iterations):
            x_new = adj_matrix @ x
            norm = np.linalg.norm(x_new)
            
            if norm > 0:
                x_new /= norm
            
            if np.linalg.norm(x_new - x) < tolerance:
                break
            
            x = x_new
        
        # Map back to node IDs
        centrality = {node: float(x[node_to_idx[node]]) for node in nodes}
        
        return centrality
    
    def spread_potential(self, source_node: str, max_hops: int = 3) -> Dict[str, any]:
        """
        Compute the spread potential if a node becomes infected.
        
        Measures reachability and direct influence within neighborhood.
        
        Args:
            source_node: The user node to analyze
            max_hops: Maximum hops to consider for spread
        
        Returns:
            Dictionary with spread metrics
        """
        if source_node not in self.graph.nodes:
            raise ValueError(f"Node {source_node} not in graph")
        
        # BFS to find reachable nodes
        visited = set()
        queue = deque([(source_node, 0)])
        visited.add(source_node)
        hop_distribution = {}
        
        while queue:
            node, hop = queue.popleft()
            
            if hop <= max_hops:
                hop_distribution[hop] = hop_distribution.get(hop, 0) + 1
                
                for neighbor in self.graph.get_neighbors(node):
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, hop + 1))
        
        reachable = len(visited) - 1  # Exclude source
        
        return {
            'source_node': source_node,
            'directly_reachable': len(self.graph.get_neighbors(source_node)),
            'total_reachable': reachable,
            'hop_distribution': hop_distribution,
            'reachability_rate': reachable / (self.graph.get_node_count() - 1) if self.graph.get_node_count() > 1 else 0
        }
    
    def identify_influential_spreaders(self, top_k: int = 10, method: str = 'combined') -> List[Tuple[str, float]]:
        """
        Identify top K most influential spreaders.
        
        Args:
            top_k: Number of top spreaders to return
            method: 'degree', 'betweenness', 'eigenvector', or 'combined'
        
        Returns:
            List of (node_id, influence_score) tuples, sorted by influence
        """
        if method == 'degree':
            scores = self.degree_centrality()
        elif method == 'betweenness':
            scores = self.betweenness_centrality()
        elif method == 'eigenvector':
            scores = self.eigenvector_centrality()
        elif method == 'combined':
            # Normalize and combine multiple metrics
            degree = self.degree_centrality()
            betweenness = self.betweenness_centrality(sample_size=100)
            eigenvector = self.eigenvector_centrality()
            
            # Normalize each metric to [0, 1]
            def normalize(metrics_dict):
                max_val = max(metrics_dict.values()) if metrics_dict else 1
                return {k: v / max_val if max_val > 0 else 0 for k, v in metrics_dict.items()}
            
            degree_norm = normalize(degree)
            between_norm = normalize(betweenness)
            eigen_norm = normalize(eigenvector)
            
            # Weighted combination
            scores = {}
            for node in self.graph.nodes:
                scores[node] = (0.3 * degree_norm.get(node, 0) +
                               0.4 * between_norm.get(node, 0) +
                               0.3 * eigen_norm.get(node, 0))
        else:
            raise ValueError(f"Unknown method: {method}")
        
        # Sort and return top K
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return sorted_scores[:top_k]
    
    def _find_all_shortest_paths(self, source: str, target: str) -> List[List[str]]:
        """Find all shortest paths between two nodes using BFS."""
        if source == target:
            return [[source]]
        
        # BFS to find distances
        distances = {source: 0}
        queue = deque([source])
        
        while queue:
            node = queue.popleft()
            for neighbor in self.graph.get_neighbors(node):
                if neighbor not in distances:
                    distances[neighbor] = distances[node] + 1
                    queue.append(neighbor)
        
        if target not in distances:
            return []
        
        # Reconstruct all shortest paths
        target_dist = distances[target]
        paths = []
        
        def dfs(node, path):
            if node == target:
                paths.append(path)
                return
            
            if len(path) - 1 < target_dist:
                for neighbor in self.graph.get_neighbors(node):
                    if neighbor in distances and distances[neighbor] == distances[node] + 1:
                        dfs(neighbor, path + [neighbor])
        
        dfs(source, [source])
        return paths
    
    def _bfs_distances(self, source: str) -> Dict[str, int]:
        """Compute shortest distances from source to all nodes using BFS."""
        distances = {source: 0}
        queue = deque([source])
        
        while queue:
            node = queue.popleft()
            for neighbor in self.graph.get_neighbors(node):
                if neighbor not in distances:
                    distances[neighbor] = distances[node] + 1
                    queue.append(neighbor)
        
        return distances
    
    def export_metrics(self, output_dir: str) -> None:
        """
        Export all metrics to JSON files.
        
        Args:
            output_dir: Directory to save metric files
        """
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Compute metrics
        print("Computing degree centrality...")
        degree = self.degree_centrality()
        
        print("Computing in-degree centrality...")
        in_degree = self.in_degree_centrality()
        
        print("Computing closeness centrality...")
        closeness = self.closeness_centrality()
        
        print("Computing eigenvector centrality...")
        eigenvector = self.eigenvector_centrality()
        
        print("Computing betweenness centrality (sampled)...")
        betweenness = self.betweenness_centrality(sample_size=100)
        
        # Save individual metrics
        metrics_data = {
            'degree_centrality': degree,
            'in_degree_centrality': in_degree,
            'closeness_centrality': closeness,
            'eigenvector_centrality': eigenvector,
            'betweenness_centrality': betweenness
        }
        
        with open(f'{output_dir}/centrality_metrics.json', 'w') as f:
            json.dump(metrics_data, f, indent=2)
        
        # Find and save influential spreaders
        print("Identifying influential spreaders...")
        influential = self.identify_influential_spreaders(top_k=20, method='combined')
        
        influential_data = {
            'top_spreaders': [{'user_id': uid, 'influence_score': score} 
                             for uid, score in influential]
        }
        
        with open(f'{output_dir}/influential_spreaders.json', 'w') as f:
            json.dump(influential_data, f, indent=2)
        
        print(f"Metrics saved to {output_dir}/")


def main():
    """Example usage of PropagationMetrics."""
    from build_graph import SocialNetworkGraph
    
    print("Loading social network graph...")
    graph = SocialNetworkGraph()
    graph.load_from_csv('data/processed/clean_data.csv')
    
    print("Computing propagation metrics...")
    metrics = PropagationMetrics(graph)
    
    # Get influential spreaders
    print("\n=== Top 10 Influential Spreaders (Combined Method) ===")
    influential = metrics.identify_influential_spreaders(top_k=10, method='combined')
    for rank, (user_id, score) in enumerate(influential, 1):
        print(f"{rank}. {user_id}: {score:.4f}")
    
    # Analyze a specific spreader
    if influential:
        top_spreader = influential[0][0]
        print(f"\n=== Spread Potential for {top_spreader} ===")
        spread = metrics.spread_potential(top_spreader)
        print(f"Directly reachable: {spread['directly_reachable']}")
        print(f"Total reachable (3 hops): {spread['total_reachable']}")
        print(f"Reachability rate: {spread['reachability_rate']:.2%}")
    
    # Export all metrics
    metrics.export_metrics('data/processed/metrics')


if __name__ == '__main__':
    main()
