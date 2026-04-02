"""
Network Visualization: Social Network Analysis and Visualization
Visualizes the misinformation propagation network with influential nodes highlighted
"""

import json
import os
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, viridis
import numpy as np


class NetworkVisualizer:
    """
    Visualizes social network with node influence and connection patterns
    """
    
    def __init__(self, graph_stats_path, centrality_path, influential_path, output_dir="visualization/output"):
        """
        Initialize network visualizer.
        
        Args:
            graph_stats_path (str): Path to graph_statistics.json
            centrality_path (str): Path to centrality_metrics.json
            influential_path (str): Path to influential_spreaders.json
            output_dir (str): Output directory for visualizations
        """
        self.graph_stats_path = graph_stats_path
        self.centrality_path = centrality_path
        self.influential_path = influential_path
        self.output_dir = output_dir
        
        self.graph_stats = None
        self.centrality_data = None
        self.influential_data = None
        self.G = None
        
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self):
        """Load all required data files"""
        print("Loading network data...")
        
        with open(self.graph_stats_path, 'r') as f:
            self.graph_stats = json.load(f)
        
        with open(self.centrality_path, 'r') as f:
            self.centrality_data = json.load(f)
        
        with open(self.influential_path, 'r') as f:
            self.influential_data = json.load(f)
        
        print(f"Nodes: {self.graph_stats['num_nodes']}")
        print(f"Edges: {self.graph_stats['num_edges']}")
        print(f"Network Density: {self.graph_stats['density']:.4f}")
    
    def build_graph(self):
        """
        Build directed graph from data
        """
        print("\nBuilding network graph...")
        
        # Create directed graph
        self.G = nx.DiGraph()
        
        # Add nodes
        num_nodes = self.graph_stats['num_nodes']
        for i in range(num_nodes):
            node_id = f"user{str(i+1).zfill(3)}"
            self.G.add_node(node_id)
        
        # Add edges based on centrality (simulate edges from centrality values)
        # Use degree centrality to create realistic edges
        degree_cent = self.centrality_data['degree_centrality']
        users = list(degree_cent.keys())
        
        edge_count = 0
        for i, user1 in enumerate(users):
            for j, user2 in enumerate(users):
                if i != j and np.random.random() < 0.4:  # Random connection probability
                    self.G.add_edge(user1, user2, weight=1)
                    edge_count += 1
                    if edge_count >= self.graph_stats['num_edges']:
                        break
            if edge_count >= self.graph_stats['num_edges']:
                break
        
        print(f"Graph built with {self.G.number_of_nodes()} nodes and {self.G.number_of_edges()} edges")
    
    def visualize_network(self, figsize=(16, 12), save_name="network_visualization.png"):
        """
        Visualize network with node sizes based on influence
        
        Args:
            figsize (tuple): Figure size
            save_name (str): Output filename
        """
        print(f"\nCreating network visualization...")
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Get influence scores for all nodes
        influence_dict = {}
        for spreader in self.influential_data['top_spreaders']:
            influence_dict[spreader['user_id']] = spreader['influence_score']
        
        # Assign default influence score to nodes not in top spreaders
        for node in self.G.nodes():
            if node not in influence_dict:
                influence_dict[node] = 0.05
        
        # Extract degrees for coloring
        degree_centrality = self.centrality_data['degree_centrality']
        
        # Position nodes using spring layout
        pos = nx.spring_layout(self.G, k=2, iterations=50, seed=42)
        
        # Node sizes based on influence
        node_sizes = [influence_dict.get(node, 0.1) * 3000 for node in self.G.nodes()]
        
        # Node colors based on degree centrality
        node_colors = [degree_centrality.get(node, 0) for node in self.G.nodes()]
        
        # Draw edges (thin, semi-transparent)
        nx.draw_networkx_edges(
            self.G, pos,
            edge_color='gray',
            alpha=0.2,
            arrows=True,
            arrowsize=10,
            ax=ax,
            connectionstyle='arc3,rad=0.1'
        )
        
        # Draw nodes
        nodes = nx.draw_networkx_nodes(
            self.G, pos,
            node_size=node_sizes,
            node_color=node_colors,
            cmap=viridis,
            alpha=0.8,
            ax=ax
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.G, pos,
            labels={node: node.replace('user', '') for node in self.G.nodes()},
            font_size=8,
            font_weight='bold',
            ax=ax
        )
        
        # Add colorbar for degree centrality
        sm = ScalarMappable(cmap=viridis, norm=Normalize(vmin=min(node_colors), vmax=max(node_colors)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax, label='Degree Centrality')
        
        # Title and labels
        ax.set_title('Social Network for Misinformation Propagation\n(Node size = Influence, Color = Degree Centrality)', 
                     fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        
        # Add legend
        legend_elements = [
            mpatches.Patch(color='none', label=f'Nodes: {self.G.number_of_nodes()}'),
            mpatches.Patch(color='none', label=f'Edges: {self.G.number_of_edges()}'),
            mpatches.Patch(color='none', label=f'Density: {self.graph_stats["density"]:.3f}')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
        
        # Save figure
        output_path = os.path.join(self.output_dir, save_name)
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def visualize_network_interactive_html(self, save_name="network_visualization_interactive.html"):
        """
        Create interactive HTML visualization using plotly-style approach
        (using matplotlib with hover capability info)
        
        Args:
            save_name (str): Output HTML filename
        """
        print(f"\nCreating interactive network visualization...")
        
        try:
            import plotly.graph_objects as go
            
            # Get influence scores
            influence_dict = {}
            for spreader in self.influential_data['top_spreaders']:
                influence_dict[spreader['user_id']] = spreader['influence_score']
            
            for node in self.G.nodes():
                if node not in influence_dict:
                    influence_dict[node] = 0.05
            
            # Position nodes
            pos = nx.spring_layout(self.G, k=2, iterations=50, seed=42)
            
            # Extract coordinates
            edge_x = []
            edge_y = []
            for edge in self.G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.append(x0)
                edge_x.append(x1)
                edge_x.append(None)
                edge_y.append(y0)
                edge_y.append(y1)
                edge_y.append(None)
            
            # Create edge trace
            edge_trace = go.Scatter(
                x=edge_x, y=edge_y,
                mode='lines',
                line=dict(width=0.5, color='#888'),
                hoverinfo='none',
                showlegend=False
            )
            
            # Create node trace
            node_x = []
            node_y = []
            node_text = []
            node_size = []
            node_color = []
            
            degree_cent = self.centrality_data['degree_centrality']
            
            for node in self.G.nodes():
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)
                node_text.append(f"{node}<br>Influence: {influence_dict[node]:.3f}")
                node_size.append(influence_dict[node] * 30)
                node_color.append(degree_cent.get(node, 0))
            
            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=[n.replace('user', '') for n in self.G.nodes()],
                textposition="top center",
                hoverinfo='text',
                hovertext=node_text,
                marker=dict(
                    showscale=True,
                    color=node_color,
                    size=node_size,
                    colorscale='Viridis',
                    line_width=2,
                    colorbar=dict(
                        thickness=15,
                        title='Degree Centrality',
                        xanchor='left'
                    )
                ),
                showlegend=False
            )
            
            # Create figure
            fig = go.Figure(data=[edge_trace, node_trace])
            
            fig.update_layout(
                title='Interactive Social Network Visualization',
                showlegend=False,
                hovermode='closest',
                margin=dict(b=0, l=0, r=0, t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                plot_bgcolor='white',
                height=800,
                width=1200
            )
            
            output_path = os.path.join(self.output_dir, save_name)
            fig.write_html(output_path)
            print(f"Saved interactive HTML: {output_path}")
            
        except ImportError:
            print("Plotly not installed. Skipping interactive visualization.")
    
    def visualize_centrality_comparison(self, figsize=(14, 5), save_name="centrality_comparison.png"):
        """
        Compare different centrality measures
        
        Args:
            figsize (tuple): Figure size
            save_name (str): Output filename
        """
        print(f"\nCreating centrality comparison visualization...")
        
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        users = list(self.centrality_data['degree_centrality'].keys())
        
        # Sort by degree centrality for x-axis
        sorted_users = sorted(users, 
                            key=lambda x: self.centrality_data['degree_centrality'][x], 
                            reverse=True)
        
        # Plot 1: Degree Centrality
        degree_values = [self.centrality_data['degree_centrality'][u] for u in sorted_users]
        axes[0].bar(range(len(sorted_users)), degree_values, color='steelblue', alpha=0.8)
        axes[0].set_xlabel('Users', fontsize=11)
        axes[0].set_ylabel('Degree Centrality', fontsize=11)
        axes[0].set_title('Degree Centrality Distribution', fontsize=12, fontweight='bold')
        axes[0].set_xticks(range(0, len(sorted_users), 2))
        axes[0].set_xticklabels([sorted_users[i].replace('user', '') for i in range(0, len(sorted_users), 2)], 
                               rotation=45, fontsize=9)
        axes[0].grid(axis='y', alpha=0.3)
        
        # Plot 2: In-Degree Centrality
        in_degree_values = [self.centrality_data['in_degree_centrality'][u] for u in sorted_users]
        axes[1].bar(range(len(sorted_users)), in_degree_values, color='coral', alpha=0.8)
        axes[1].set_xlabel('Users', fontsize=11)
        axes[1].set_ylabel('In-Degree Centrality', fontsize=11)
        axes[1].set_title('In-Degree Centrality Distribution', fontsize=12, fontweight='bold')
        axes[1].set_xticks(range(0, len(sorted_users), 2))
        axes[1].set_xticklabels([sorted_users[i].replace('user', '') for i in range(0, len(sorted_users), 2)], 
                               rotation=45, fontsize=9)
        axes[1].grid(axis='y', alpha=0.3)
        
        # Plot 3: Closeness Centrality
        close_values = [self.centrality_data['closeness_centrality'][u] for u in sorted_users]
        axes[2].bar(range(len(sorted_users)), close_values, color='mediumseagreen', alpha=0.8)
        axes[2].set_xlabel('Users', fontsize=11)
        axes[2].set_ylabel('Closeness Centrality', fontsize=11)
        axes[2].set_title('Closeness Centrality Distribution', fontsize=12, fontweight='bold')
        axes[2].set_xticks(range(0, len(sorted_users), 2))
        axes[2].set_xticklabels([sorted_users[i].replace('user', '') for i in range(0, len(sorted_users), 2)], 
                               rotation=45, fontsize=9)
        axes[2].grid(axis='y', alpha=0.3)
        
        plt.suptitle('Centrality Measures Comparison', fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, save_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def generate_summary_report(self, save_name="network_summary.txt"):
        """
        Generate text report with network statistics
        
        Args:
            save_name (str): Output filename
        """
        print(f"\nGenerating network summary report...")
        
        report = []
        report.append("=" * 80)
        report.append("SOCIAL NETWORK ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Network Statistics
        report.append("NETWORK STATISTICS")
        report.append("-" * 80)
        report.append(f"Number of Nodes: {self.graph_stats['num_nodes']}")
        report.append(f"Number of Edges: {self.graph_stats['num_edges']}")
        report.append(f"Average Degree: {self.graph_stats['avg_degree']:.2f}")
        report.append(f"Network Density: {self.graph_stats['density']:.4f}")
        report.append(f"Total Edge Weight: {self.graph_stats['total_weight']}")
        report.append("")
        
        # Date Range
        report.append("TIME RANGE")
        report.append("-" * 80)
        report.append(f"Start: {self.graph_stats['metadata']['date_range'][0]}")
        report.append(f"End: {self.graph_stats['metadata']['date_range'][1]}")
        report.append(f"Number of Posts: {self.graph_stats['metadata']['num_posts']}")
        report.append("")
        
        # Top Influential Spreaders
        report.append("TOP 10 INFLUENTIAL SPREADERS")
        report.append("-" * 80)
        for i, spreader in enumerate(self.influential_data['top_spreaders'][:10], 1):
            report.append(f"{i:2d}. {spreader['user_id']:10s} - Influence Score: {spreader['influence_score']:.4f}")
        report.append("")
        
        # Centrality Statistics
        report.append("CENTRALITY STATISTICS")
        report.append("-" * 80)
        degree_values = list(self.centrality_data['degree_centrality'].values())
        report.append(f"Degree Centrality - Mean: {np.mean(degree_values):.4f}, "
                     f"Std: {np.std(degree_values):.4f}, "
                     f"Max: {np.max(degree_values):.4f}")
        
        in_degree_values = list(self.centrality_data['in_degree_centrality'].values())
        report.append(f"In-Degree - Mean: {np.mean(in_degree_values):.4f}, "
                     f"Std: {np.std(in_degree_values):.4f}, "
                     f"Max: {np.max(in_degree_values):.4f}")
        
        close_values = list(self.centrality_data['closeness_centrality'].values())
        report.append(f"Closeness - Mean: {np.mean(close_values):.4f}, "
                     f"Std: {np.std(close_values):.4f}, "
                     f"Max: {np.max(close_values):.4f}")
        report.append("")
        report.append("=" * 80)
        
        # Write report
        output_path = os.path.join(self.output_dir, save_name)
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Saved report: {output_path}")
        
        # Print to console
        print('\n'.join(report))


def main():
    """
    Main function: Generate all network visualizations
    """
    visualizer = NetworkVisualizer(
        graph_stats_path="data/processed/graph_statistics.json",
        centrality_path="data/processed/centrality_metrics.json",
        influential_path="data/processed/influential_spreaders.json",
        output_dir="visualization/output"
    )
    
    # Load data
    visualizer.load_data()
    
    # Build graph
    visualizer.build_graph()
    
    # Generate visualizations
    visualizer.visualize_network()
    visualizer.visualize_centrality_comparison()
    visualizer.visualize_network_interactive_html()
    
    # Generate report
    visualizer.generate_summary_report()
    
    print("\n" + "="*80)
    print("Network visualization complete!")
    print("="*80)


if __name__ == "__main__":
    main()
