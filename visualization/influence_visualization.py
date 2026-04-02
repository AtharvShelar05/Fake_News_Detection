"""
Influence Visualization: Influential Spreaders Analysis
Visualizes influential users and centrality distributions
"""

import json
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from matplotlib.cm import ScalarMappable, RdYlGn_r


class InfluenceVisualizer:
    """
    Visualizes influence metrics and top spreaders
    """
    
    def __init__(self, influential_path, centrality_path, output_dir="visualization/output"):
        """
        Initialize influence visualizer.
        
        Args:
            influential_path (str): Path to influential_spreaders.json
            centrality_path (str): Path to centrality_metrics.json
            output_dir (str): Output directory for visualizations
        """
        self.influential_path = influential_path
        self.centrality_path = centrality_path
        self.output_dir = output_dir
        
        self.influential_data = None
        self.centrality_data = None
        
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self):
        """Load all required data files"""
        print("Loading influence data...")
        
        with open(self.influential_path, 'r') as f:
            self.influential_data = json.load(f)
        
        with open(self.centrality_path, 'r') as f:
            self.centrality_data = json.load(f)
        
        print(f"Loaded {len(self.influential_data['top_spreaders'])} spreaders")
    
    def visualize_top_spreaders(self, top_n=10, figsize=(12, 7), save_name="top_spreaders.png"):
        """
        Create bar chart of top influential spreaders
        
        Args:
            top_n (int): Number of top spreaders to display
            figsize (tuple): Figure size
            save_name (str): Output filename
        """
        print(f"\nCreating top {top_n} spreaders visualization...")
        
        # Get top spreaders
        top_spreaders = self.influential_data['top_spreaders'][:top_n]
        
        users = [s['user_id'] for s in top_spreaders]
        scores = [s['influence_score'] for s in top_spreaders]
        
        # Create figure
        fig, ax = plt.subplots(figsize=figsize)
        
        # Create color gradient
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(users)))
        
        # Create bar chart
        bars = ax.barh(users, scores, color=colors, edgecolor='black', linewidth=1.5, alpha=0.85)
        
        # Add value labels on bars
        for i, (bar, score) in enumerate(zip(bars, scores)):
            ax.text(score + 0.01, bar.get_y() + bar.get_height()/2, 
                   f'{score:.4f}', va='center', fontsize=10, fontweight='bold')
        
        # Customize plot
        ax.set_xlabel('Influence Score', fontsize=12, fontweight='bold')
        ax.set_ylabel('User ID', fontsize=12, fontweight='bold')
        ax.set_title(f'Top {top_n} Most Influential Spreaders', fontsize=14, fontweight='bold', pad=20)
        ax.grid(axis='x', alpha=0.3, linestyle='--')
        ax.set_xlim(0, max(scores) * 1.15)
        
        # Add statistics
        avg_score = np.mean(scores)
        max_score = max(scores)
        ax.axvline(avg_score, color='blue', linestyle='--', linewidth=2, alpha=0.7, label=f'Average: {avg_score:.4f}')
        ax.legend(fontsize=10, loc='lower right')
        
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.output_dir, save_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def visualize_all_spreaders(self, figsize=(14, 8), save_name="all_spreaders.png"):
        """
        Create scatter plot of all spreaders by rank and score
        
        Args:
            figsize (tuple): Figure size
            save_name (str): Output filename
        """
        print(f"\nCreating all spreaders visualization...")
        
        spreaders = self.influential_data['top_spreaders']
        
        ranks = np.arange(1, len(spreaders) + 1)
        scores = [s['influence_score'] for s in spreaders]
        user_ids = [s['user_id'] for s in spreaders]
        
        # Create figure with 2 subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Plot 1: Scatter with color gradient
        colors = plt.cm.viridis(np.linspace(0, 1, len(spreaders)))
        scatter = ax1.scatter(ranks, scores, c=range(len(spreaders)), cmap='viridis', 
                             s=200, alpha=0.7, edgecolors='black', linewidth=1.5)
        
        # Add user labels to top 5
        for i in range(min(5, len(spreaders))):
            ax1.annotate(user_ids[i], (ranks[i], scores[i]), 
                        textcoords="offset points", xytext=(0,10), 
                        ha='center', fontsize=9, fontweight='bold')
        
        ax1.set_xlabel('Rank', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Influence Score', fontsize=12, fontweight='bold')
        ax1.set_title('Influence Score by Rank', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        ax1.invert_xaxis()  # Higher rank on left = more influential
        
        cbar1 = plt.colorbar(scatter, ax=ax1)
        cbar1.set_label('Rank', fontsize=10)
        
        # Plot 2: Distribution histogram
        ax2.hist(scores, bins=15, color='steelblue', alpha=0.7, edgecolor='black', linewidth=1.5)
        ax2.axvline(np.mean(scores), color='red', linestyle='--', linewidth=2.5, label=f'Mean: {np.mean(scores):.4f}')
        ax2.axvline(np.median(scores), color='green', linestyle='--', linewidth=2.5, label=f'Median: {np.median(scores):.4f}')
        
        ax2.set_xlabel('Influence Score', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Frequency', fontsize=12, fontweight='bold')
        ax2.set_title('Distribution of Influence Scores', fontsize=13, fontweight='bold')
        ax2.legend(fontsize=10)
        ax2.grid(axis='y', alpha=0.3)
        
        plt.suptitle('Influence Score Analysis - All Users', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.output_dir, save_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def visualize_centrality_distributions(self, figsize=(15, 5), save_name="centrality_distributions.png"):
        """
        Create distribution plots for all centrality measures
        
        Args:
            figsize (tuple): Figure size
            save_name (str): Output filename
        """
        print(f"\nCreating centrality distributions visualization...")
        
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        measures = {
            'Degree Centrality': self.centrality_data['degree_centrality'],
            'In-Degree Centrality': self.centrality_data['in_degree_centrality'],
            'Closeness Centrality': self.centrality_data['closeness_centrality']
        }
        
        colors_list = ['steelblue', 'coral', 'mediumseagreen']
        
        for idx, (measure_name, measure_data) in enumerate(measures.items()):
            values = list(measure_data.values())
            
            ax = axes[idx]
            
            # Histogram
            n, bins, patches = ax.hist(values, bins=12, color=colors_list[idx], 
                                       alpha=0.7, edgecolor='black', linewidth=1.5)
            
            # Color bars by intensity
            cm = plt.cm.RdYlGn(np.linspace(0.2, 0.8, len(patches)))
            for patch, color in zip(patches, cm):
                patch.set_facecolor(color)
            
            # Add statistics lines
            mean_val = np.mean(values)
            median_val = np.median(values)
            
            ax.axvline(mean_val, color='red', linestyle='--', linewidth=2, label=f'Mean: {mean_val:.3f}')
            ax.axvline(median_val, color='blue', linestyle='--', linewidth=2, label=f'Median: {median_val:.3f}')
            
            ax.set_xlabel('Centrality Value', fontsize=11, fontweight='bold')
            ax.set_ylabel('Frequency', fontsize=11, fontweight='bold')
            ax.set_title(f'{measure_name} Distribution', fontsize=12, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(axis='y', alpha=0.3)
            
            # Add statistical info
            stats_text = f'Min: {min(values):.3f}\nMax: {max(values):.3f}\nStd: {np.std(values):.3f}'
            ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, 
                   fontsize=9, verticalalignment='top', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.suptitle('Centrality Measures - Distribution Analysis', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.output_dir, save_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def visualize_influence_vs_centrality(self, figsize=(14, 6), save_name="influence_vs_centrality.png"):
        """
        Compare influence scores with centrality measures
        
        Args:
            figsize (tuple): Figure size
            save_name (str): Output filename
        """
        print(f"\nCreating influence vs centrality visualization...")
        
        # Get influence scores for all users
        influence_dict = {}
        for spreader in self.influential_data['top_spreaders']:
            influence_dict[spreader['user_id']] = spreader['influence_score']
        
        # Extract centrality values
        users = list(self.centrality_data['degree_centrality'].keys())
        
        # Create data for plotting
        degree_vals = [self.centrality_data['degree_centrality'].get(u, 0) for u in users]
        in_degree_vals = [self.centrality_data['in_degree_centrality'].get(u, 0) for u in users]
        close_vals = [self.centrality_data['closeness_centrality'].get(u, 0) for u in users]
        influence_vals = [influence_dict.get(u, 0.01) for u in users]
        
        # Create figure
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        # Plot 1: Degree Centrality vs Influence
        axes[0].scatter(degree_vals, influence_vals, s=150, alpha=0.6, 
                       c=influence_vals, cmap='RdYlGn_r', edgecolors='black', linewidth=1.5)
        axes[0].set_xlabel('Degree Centrality', fontsize=11, fontweight='bold')
        axes[0].set_ylabel('Influence Score', fontsize=11, fontweight='bold')
        axes[0].set_title('Degree Centrality vs Influence', fontsize=12, fontweight='bold')
        axes[0].grid(True, alpha=0.3)
        
        # Add correlation
        corr_degree = np.corrcoef(degree_vals, influence_vals)[0, 1]
        axes[0].text(0.05, 0.95, f'Correlation: {corr_degree:.3f}', 
                    transform=axes[0].transAxes, fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                    verticalalignment='top')
        
        # Plot 2: In-Degree Centrality vs Influence
        axes[1].scatter(in_degree_vals, influence_vals, s=150, alpha=0.6, 
                       c=influence_vals, cmap='RdYlGn_r', edgecolors='black', linewidth=1.5)
        axes[1].set_xlabel('In-Degree Centrality', fontsize=11, fontweight='bold')
        axes[1].set_ylabel('Influence Score', fontsize=11, fontweight='bold')
        axes[1].set_title('In-Degree Centrality vs Influence', fontsize=12, fontweight='bold')
        axes[1].grid(True, alpha=0.3)
        
        corr_in_degree = np.corrcoef(in_degree_vals, influence_vals)[0, 1]
        axes[1].text(0.05, 0.95, f'Correlation: {corr_in_degree:.3f}', 
                    transform=axes[1].transAxes, fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                    verticalalignment='top')
        
        # Plot 3: Closeness Centrality vs Influence
        axes[2].scatter(close_vals, influence_vals, s=150, alpha=0.6, 
                       c=influence_vals, cmap='RdYlGn_r', edgecolors='black', linewidth=1.5)
        axes[2].set_xlabel('Closeness Centrality', fontsize=11, fontweight='bold')
        axes[2].set_ylabel('Influence Score', fontsize=11, fontweight='bold')
        axes[2].set_title('Closeness Centrality vs Influence', fontsize=12, fontweight='bold')
        axes[2].grid(True, alpha=0.3)
        
        corr_closeness = np.corrcoef(close_vals, influence_vals)[0, 1]
        axes[2].text(0.05, 0.95, f'Correlation: {corr_closeness:.3f}', 
                    transform=axes[2].transAxes, fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5),
                    verticalalignment='top')
        
        plt.suptitle('Influence Scores vs Network Centrality Measures', fontsize=14, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        # Save figure
        output_path = os.path.join(self.output_dir, save_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def generate_influence_report(self, save_name="influence_report.txt"):
        """
        Generate comprehensive influence analysis report
        
        Args:
            save_name (str): Output filename
        """
        print(f"\nGenerating influence analysis report...")
        
        report = []
        report.append("=" * 80)
        report.append("INFLUENCE AND CENTRALITY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        # Top Spreaders
        report.append("TOP 15 INFLUENTIAL SPREADERS")
        report.append("-" * 80)
        for i, spreader in enumerate(self.influential_data['top_spreaders'][:15], 1):
            report.append(f"{i:2d}. {spreader['user_id']:10s} - Influence Score: {spreader['influence_score']:.6f}")
        report.append("")
        
        # Influence Statistics
        influence_scores = [s['influence_score'] for s in self.influential_data['top_spreaders']]
        report.append("INFLUENCE SCORE STATISTICS")
        report.append("-" * 80)
        report.append(f"Mean: {np.mean(influence_scores):.6f}")
        report.append(f"Median: {np.median(influence_scores):.6f}")
        report.append(f"Std Dev: {np.std(influence_scores):.6f}")
        report.append(f"Min: {np.min(influence_scores):.6f}")
        report.append(f"Max: {np.max(influence_scores):.6f}")
        report.append(f"Range: {np.max(influence_scores) - np.min(influence_scores):.6f}")
        report.append("")
        
        # Centrality Statistics
        report.append("CENTRALITY STATISTICS")
        report.append("-" * 80)
        
        for measure_name, measure_data in self.centrality_data.items():
            values = list(measure_data.values())
            report.append(f"\n{measure_name}:")
            report.append(f"  Mean: {np.mean(values):.6f}")
            report.append(f"  Median: {np.median(values):.6f}")
            report.append(f"  Std Dev: {np.std(values):.6f}")
            report.append(f"  Min: {np.min(values):.6f}")
            report.append(f"  Max: {np.max(values):.6f}")
        
        report.append("")
        report.append("=" * 80)
        
        # Write report
        output_path = os.path.join(self.output_dir, save_name)
        with open(output_path, 'w') as f:
            f.write('\n'.join(report))
        
        print(f"Saved report: {output_path}")
        print('\n'.join(report))


def main():
    """
    Main function: Generate all influence visualizations
    """
    visualizer = InfluenceVisualizer(
        influential_path="data/processed/influential_spreaders.json",
        centrality_path="data/processed/centrality_metrics.json",
        output_dir="visualization/output"
    )
    
    # Load data
    visualizer.load_data()
    
    # Generate visualizations
    visualizer.visualize_top_spreaders(top_n=10)
    visualizer.visualize_all_spreaders()
    visualizer.visualize_centrality_distributions()
    visualizer.visualize_influence_vs_centrality()
    
    # Generate report
    visualizer.generate_influence_report()
    
    print("\n" + "="*80)
    print("Influence visualization complete!")
    print("="*80)


if __name__ == "__main__":
    main()
