"""
Diffusion Visualization: SIR Model Trajectories
Visualizes misinformation spread dynamics using SIR (Susceptible-Infected-Recovered) model
"""

import json
import os
import glob
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.patches as mpatches


class DiffusionVisualizer:
    """
    Visualizes information diffusion trajectories under different infection probabilities
    """
    
    def __init__(self, diffusion_data_dir="data/processed", output_dir="visualization/output"):
        """
        Initialize diffusion visualizer.
        
        Args:
            diffusion_data_dir (str): Directory containing diffusion_trajectory_prob*.json files
            output_dir (str): Output directory for visualizations
        """
        self.diffusion_data_dir = diffusion_data_dir
        self.output_dir = output_dir
        self.trajectories = {}
        
        os.makedirs(output_dir, exist_ok=True)
    
    def load_trajectories(self):
        """
        Load all diffusion trajectory files
        """
        print("Loading diffusion trajectories...")
        
        # Find all trajectory files
        pattern = os.path.join(self.diffusion_data_dir, "diffusion_trajectory_prob*.json")
        files = sorted(glob.glob(pattern))
        
        for filepath in files:
            # Extract probability from filename
            filename = os.path.basename(filepath)
            prob = filename.replace("diffusion_trajectory_prob", "").replace(".json", "")
            
            with open(filepath, 'r') as f:
                data = json.load(f)
            
            self.trajectories[prob] = data
            print(f"  Loaded: {filename}")
        
        if not self.trajectories:
            print("WARNING: No trajectory files found!")
        else:
            print(f"Successfully loaded {len(self.trajectories)} trajectories")
    
    def parse_trajectory(self, trajectory_data):
        """
        Parse trajectory data into S, I, R arrays
        
        Args:
            trajectory_data (dict): Trajectory data with 'trajectory' key
            
        Returns:
            tuple: (time_points, S_values, I_values, R_values)
        """
        trajectory = trajectory_data['trajectory']
        
        time_points = []
        S_values = []
        I_values = []
        R_values = []
        
        for i, (s, i, r) in enumerate(trajectory):
            time_points.append(i)
            S_values.append(s)
            I_values.append(i)
            R_values.append(r)
        
        return time_points, S_values, I_values, R_values
    
    def visualize_single_trajectory(self, prob_key, figsize=(12, 6), save_name=None):
        """
        Visualize single SIR trajectory
        
        Args:
            prob_key (str): Probability key (e.g., '0.1', '0.2')
            figsize (tuple): Figure size
            save_name (str): Output filename (auto-generated if None)
        """
        if prob_key not in self.trajectories:
            print(f"WARNING: Trajectory for {prob_key} not found")
            return
        
        print(f"\nVisualizing trajectory for probability {prob_key}...")
        
        trajectory_data = self.trajectories[prob_key]
        time_points, S_values, I_values, R_values = self.parse_trajectory(trajectory_data)
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=figsize)
        
        # Plot 1: Stacked area chart
        ax1.fill_between(time_points, 0, S_values, label='Susceptible (S)', 
                        color='#1f77b4', alpha=0.7)
        ax1.fill_between(time_points, S_values, np.array(S_values) + np.array(I_values), 
                        label='Infected (I)', color='#ff7f0e', alpha=0.7)
        ax1.fill_between(time_points, np.array(S_values) + np.array(I_values), 
                        np.array(S_values) + np.array(I_values) + np.array(R_values),
                        label='Recovered (R)', color='#2ca02c', alpha=0.7)
        
        ax1.set_xlabel('Time (steps)', fontsize=12)
        ax1.set_ylabel('Population', fontsize=12)
        ax1.set_title(f'SIR Diffusion Trajectory (Infection Probability: {prob_key})\nStacked Area Chart', 
                     fontsize=13, fontweight='bold')
        ax1.legend(loc='right', fontsize=11)
        ax1.grid(axis='y', alpha=0.3)
        ax1.set_xlim(0, len(time_points)-1)
        
        # Plot 2: Line chart
        ax2.plot(time_points, S_values, marker='o', label='Susceptible (S)', 
                linewidth=2, markersize=4, color='#1f77b4')
        ax2.plot(time_points, I_values, marker='s', label='Infected (I)', 
                linewidth=2, markersize=4, color='#ff7f0e')
        ax2.plot(time_points, R_values, marker='^', label='Recovered (R)', 
                linewidth=2, markersize=4, color='#2ca02c')
        
        ax2.set_xlabel('Time (steps)', fontsize=12)
        ax2.set_ylabel('Population', fontsize=12)
        ax2.set_title('SIR Components - Line Chart', fontsize=13, fontweight='bold')
        ax2.legend(loc='right', fontsize=11)
        ax2.grid(True, alpha=0.3)
        ax2.set_xlim(0, len(time_points)-1)
        
        plt.tight_layout()
        
        # Save figure
        if save_name is None:
            save_name = f"diffusion_trajectory_prob{prob_key}.png"
        
        output_path = os.path.join(self.output_dir, save_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def visualize_all_trajectories(self, figsize=(16, 10), save_name="all_trajectories_comparison.png"):
        """
        Visualize all trajectories for comparison
        
        Args:
            figsize (tuple): Figure size
            save_name (str): Output filename
        """
        print(f"\nCreating comparison visualization of all trajectories...")
        
        if not self.trajectories:
            print("No trajectories to visualize")
            return
        
        num_probs = len(self.trajectories)
        cols = 2
        rows = (num_probs + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=figsize)
        axes = axes.flatten() if num_probs > 1 else [axes]
        
        sorted_probs = sorted(self.trajectories.keys(), key=float)
        
        for idx, prob_key in enumerate(sorted_probs):
            trajectory_data = self.trajectories[prob_key]
            time_points, S_values, I_values, R_values = self.parse_trajectory(trajectory_data)
            
            ax = axes[idx]
            
            # Plot infected curve prominently
            ax.plot(time_points, I_values, marker='o', linewidth=2.5, 
                   markersize=5, color='#ff7f0e', label='Infected (I)')
            ax.fill_between(time_points, 0, I_values, alpha=0.3, color='#ff7f0e')
            
            # Plot other components
            ax.plot(time_points, S_values, marker='o', linewidth=1.5, 
                   markersize=3, color='#1f77b4', label='Susceptible (S)', alpha=0.7)
            ax.plot(time_points, R_values, marker='o', linewidth=1.5, 
                   markersize=3, color='#2ca02c', label='Recovered (R)', alpha=0.7)
            
            ax.set_xlabel('Time (steps)', fontsize=10)
            ax.set_ylabel('Population', fontsize=10)
            ax.set_title(f'Infection Probability: {prob_key}', fontsize=11, fontweight='bold')
            ax.legend(fontsize=9, loc='best')
            ax.grid(True, alpha=0.3)
            ax.set_xlim(0, len(time_points)-1)
        
        # Hide empty subplots
        for idx in range(num_probs, len(axes)):
            axes[idx].axis('off')
        
        plt.suptitle('SIR Diffusion Trajectories - All Scenarios', 
                    fontsize=15, fontweight='bold', y=1.00)
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, save_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def visualize_peak_comparison(self, figsize=(12, 6), save_name="peak_infection_comparison.png"):
        """
        Compare peak infection counts across different probabilities
        
        Args:
            figsize (tuple): Figure size
            save_name (str): Output filename
        """
        print(f"\nCreating peak infection comparison...")
        
        if not self.trajectories:
            print("No trajectories to compare")
            return
        
        probs = sorted(self.trajectories.keys(), key=float)
        peak_infections = []
        peak_times = []
        final_recovered = []
        
        for prob_key in probs:
            trajectory_data = self.trajectories[prob_key]
            time_points, S_values, I_values, R_values = self.parse_trajectory(trajectory_data)
            
            if I_values:
                peak_idx = np.argmax(I_values)
                peak_infections.append(max(I_values))
                peak_times.append(time_points[peak_idx])
                final_recovered.append(R_values[-1])
        
        # Create figure with 3 subplots
        fig, axes = plt.subplots(1, 3, figsize=figsize)
        
        # Plot 1: Peak Infections
        colors = plt.cm.RdYlGn_r(np.linspace(0.2, 0.8, len(probs)))
        axes[0].bar(probs, peak_infections, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        axes[0].set_xlabel('Infection Probability', fontsize=11, fontweight='bold')
        axes[0].set_ylabel('Peak Infected Count', fontsize=11, fontweight='bold')
        axes[0].set_title('Peak Infections by Probability', fontsize=12, fontweight='bold')
        axes[0].grid(axis='y', alpha=0.3)
        
        # Plot 2: Peak Infection Times
        axes[1].plot(probs, peak_times, marker='o', linewidth=2.5, markersize=8, 
                    color='steelblue', label='Peak Time')
        axes[1].fill_between(range(len(probs)), peak_times, alpha=0.3, color='steelblue')
        axes[1].set_xlabel('Infection Probability', fontsize=11, fontweight='bold')
        axes[1].set_ylabel('Time to Peak (steps)', fontsize=11, fontweight='bold')
        axes[1].set_title('Time to Peak Infection', fontsize=12, fontweight='bold')
        axes[1].set_xticks(range(len(probs)))
        axes[1].set_xticklabels(probs, rotation=45)
        axes[1].grid(True, alpha=0.3)
        
        # Plot 3: Final Recovered
        axes[2].bar(probs, final_recovered, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
        axes[2].set_xlabel('Infection Probability', fontsize=11, fontweight='bold')
        axes[2].set_ylabel('Final Recovered Count', fontsize=11, fontweight='bold')
        axes[2].set_title('Total Spread (Final Recovered)', fontsize=12, fontweight='bold')
        axes[2].grid(axis='y', alpha=0.3)
        
        plt.suptitle('Diffusion Dynamics Comparison Across Scenarios', 
                    fontsize=14, fontweight='bold', y=1.02)
        plt.tight_layout()
        
        output_path = os.path.join(self.output_dir, save_name)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Saved: {output_path}")
        plt.close()
    
    def generate_diffusion_summary(self, save_name="diffusion_summary.txt"):
        """
        Generate summary report for diffusion analysis
        
        Args:
            save_name (str): Output filename
        """
        print(f"\nGenerating diffusion summary report...")
        
        report = []
        report.append("=" * 80)
        report.append("DIFFUSION TRAJECTORY ANALYSIS REPORT")
        report.append("=" * 80)
        report.append("")
        
        sorted_probs = sorted(self.trajectories.keys(), key=float)
        
        for prob_key in sorted_probs:
            trajectory_data = self.trajectories[prob_key]
            time_points, S_values, I_values, R_values = self.parse_trajectory(trajectory_data)
            
            report.append(f"Infection Probability: {prob_key}")
            report.append("-" * 80)
            report.append(f"  Duration (timesteps): {len(time_points)}")
            report.append(f"  Peak Infected: {max(I_values)} at time {np.argmax(I_values)}")
            report.append(f"  Final Recovered: {R_values[-1]}")
            report.append(f"  Final Susceptible: {S_values[-1]}")
            report.append(f"  Total Spread Rate: {R_values[-1] / len(S_values):.2%}")
            
            # Calculate additional metrics
            if len(I_values) > 1:
                avg_infected = np.mean(I_values)
                report.append(f"  Average Infected: {avg_infected:.2f}")
            
            report.append("")
        
        # Comparison
        report.append("CROSS-SCENARIO COMPARISON")
        report.append("=" * 80)
        
        peak_infects = []
        final_recov = []
        
        for prob_key in sorted_probs:
            trajectory_data = self.trajectories[prob_key]
            _, _, I_values, R_values = self.parse_trajectory(trajectory_data)
            peak_infects.append(max(I_values))
            final_recov.append(R_values[-1])
        
        report.append(f"Highest Peak Infection: {max(peak_infects)} (Prob: {sorted_probs[np.argmax(peak_infects)]})")
        report.append(f"Lowest Peak Infection: {min(peak_infects)} (Prob: {sorted_probs[np.argmin(peak_infects)]})")
        report.append(f"Highest Final Spread: {max(final_recov)} (Prob: {sorted_probs[np.argmax(final_recov)]})")
        report.append(f"Lowest Final Spread: {min(final_recov)} (Prob: {sorted_probs[np.argmin(final_recov)]})")
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
    Main function: Generate all diffusion visualizations
    """
    visualizer = DiffusionVisualizer(
        diffusion_data_dir="data/processed",
        output_dir="visualization/output"
    )
    
    # Load trajectories
    visualizer.load_trajectories()
    
    # Generate visualizations
    for prob_key in sorted(visualizer.trajectories.keys(), key=float):
        visualizer.visualize_single_trajectory(prob_key)
    
    visualizer.visualize_all_trajectories()
    visualizer.visualize_peak_comparison()
    
    # Generate report
    visualizer.generate_diffusion_summary()
    
    print("\n" + "="*80)
    print("Diffusion visualization complete!")
    print("="*80)


if __name__ == "__main__":
    main()
