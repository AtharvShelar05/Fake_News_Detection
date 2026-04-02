"""
Misinformation Propagation Pipeline

Complete end-to-end pipeline for:
1. Building social network graphs
2. Simulating news propagation using SIR model
3. Computing influence metrics and identifying key spreaders

Run this script to execute the full propagation analysis.
"""

import sys
import os
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from propagation_model import SocialNetworkGraph, SIRDiffusionModel, PropagationMetrics


def main():
    """Run complete propagation modeling pipeline."""
    
    print("=" * 70)
    print("MISINFORMATION PROPAGATION MODELING PIPELINE")
    print("=" * 70)
    
    # Define paths
    data_path = 'data/processed/clean_data.csv'
    output_dir = 'data/processed'
    
    # ========== STEP 1: BUILD SOCIAL NETWORK GRAPH ==========
    print("\n[STEP 1] Building Social Network Graph...")
    print("-" * 70)
    
    try:
        graph = SocialNetworkGraph()
        graph.load_from_csv(data_path)
        print(f"[OK] Graph loaded successfully")
    except Exception as e:
        print(f"[ERROR] Error loading graph: {e}")
        return
    
    # Display graph statistics
    stats = graph.get_graph_statistics()
    print(f"\nGraph Statistics:")
    print(f"  - Number of users: {stats['num_nodes']}")
    print(f"  - Number of interactions: {stats['num_edges']}")
    print(f"  - Total interaction weight: {stats['total_weight']}")
    print(f"  - Average degree: {stats['avg_degree']:.2f}")
    print(f"  - Network density: {stats['density']:.6f}")
    
    # Export graph statistics
    graph.export_statistics(f'{output_dir}/graph_statistics.json')
    print(f"\n[OK] Graph statistics exported to {output_dir}/graph_statistics.json")
    
    # ========== STEP 2: COMPUTE INFLUENCE METRICS ==========
    print("\n[STEP 2] Computing Influence Metrics...")
    print("-" * 70)
    
    try:
        metrics = PropagationMetrics(graph)
        print("Computing centrality metrics (this may take a moment)...")
        
        # Export all metrics
        metrics.export_metrics(output_dir)
        print(f"[OK] Metrics exported to {output_dir}/")
        
        # Display top spreaders
        print("\nTop 15 Most Influential Spreaders (Combined Metric):")
        influential = metrics.identify_influential_spreaders(top_k=15, method='combined')
        
        for rank, (user_id, score) in enumerate(influential, 1):
            print(f"  {rank:2d}. {user_id:15s} Score: {score:.4f}")
        
    except Exception as e:
        print(f"[ERROR] Error computing metrics: {e}")
        return
    
    # ========== STEP 3: SIMULATE PROPAGATION USING SIR MODEL ==========
    print("\n[STEP 3] Simulating News Propagation (SIR Model)...")
    print("-" * 70)
    
    # Select source nodes for simulation
    source_nodes = [user for user, _ in influential[:3]]
    
    print(f"Source nodes (initial spreaders): {source_nodes}")
    
    # Run simulations with different infection probabilities
    infection_probs = [0.1, 0.2, 0.3]
    simulation_results = {}
    
    for prob in infection_probs:
        print(f"\nRunning simulation with infection_prob={prob}...")
        try:
            model = SIRDiffusionModel(
                graph,
                infection_prob=prob,
                recovery_prob=0.05
            )
            
            results = model.simulate(
                timesteps=30,
                source_nodes=source_nodes
            )
            
            simulation_results[f'infection_prob_{prob}'] = results
            
            print(f"\n  Results for infection_prob={prob}:")
            print(f"  - Peak infected: {results['peak_infected']['count']} at timestep {results['peak_infected']['timestep']}")
            print(f"  - Final infection rate: {results['final_spread']['infection_rate']:.2%}")
            print(f"  - Total infected: {results['final_spread']['total_infected']} / {results['statistics']['total_users']}")
            
            # Export trajectory
            model.export_trajectory(f'{output_dir}/diffusion_trajectory_prob{prob:.1f}.json')
            
        except Exception as e:
            print(f"  [ERROR] Error in simulation: {e}")
            continue
    
    # Save all simulation results summary
    summary = {
        'source_nodes': source_nodes,
        'simulations': simulation_results,
        'parameters': {
            'recovery_prob': 0.05,
            'infection_probs_tested': infection_probs,
            'timesteps': 30
        }
    }
    
    with open(f'{output_dir}/propagation_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n[OK] Propagation summary saved to {output_dir}/propagation_summary.json")
    
    # ========== STEP 4: ANALYZE SPREAD POTENTIAL ==========
    print("\n[STEP 4] Analyzing Spread Potential of Top Influencers...")
    print("-" * 70)
    
    spread_analysis = {}
    for rank, (user_id, score) in enumerate(influential[:5], 1):
        try:
            spread = metrics.spread_potential(user_id, max_hops=4)
            spread_analysis[user_id] = spread
            
            print(f"\n  {rank}. {user_id}:")
            print(f"     - Direct reach: {spread['directly_reachable']} users")
            print(f"     - Total reachable (4 hops): {spread['total_reachable']} users")
            print(f"     - Reachability rate: {spread['reachability_rate']:.2%}")
        except Exception as e:
            print(f"  [ERROR] Error analyzing {user_id}: {e}")
    
    with open(f'{output_dir}/spread_analysis.json', 'w') as f:
        json.dump(spread_analysis, f, indent=2)
    
    print(f"\n[OK] Spread analysis saved to {output_dir}/spread_analysis.json")
    
    # ========== FINAL SUMMARY ==========
    print("\n" + "=" * 70)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 70)
    print("\nGenerated Output Files:")
    print(f"  1. {output_dir}/graph_statistics.json")
    print(f"  2. {output_dir}/centrality_metrics.json")
    print(f"  3. {output_dir}/influential_spreaders.json")
    print(f"  4. {output_dir}/diffusion_trajectory_prob*.json (multiple)")
    print(f"  5. {output_dir}/propagation_summary.json")
    print(f"  6. {output_dir}/spread_analysis.json")
    print("\nKey Findings:")
    print(f"  - Network has {stats['num_nodes']} users and {stats['num_edges']} interactions")
    print(f"  - Identified {len(influential)} influential spreaders")
    print(f"  - Tested {len(infection_probs)} infection probability scenarios")
    print(f"  - Analyzed spread potential for top 5 influencers")
    print("\nNext Steps:")
    print("  - Review metrics in data/processed/")
    print("  - Analyze diffusion trajectories for different parameters")
    print("  - Identify optimal intervention strategies")
    print("=" * 70)


if __name__ == '__main__':
    main()
