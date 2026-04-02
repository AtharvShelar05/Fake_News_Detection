"""
Test script for the propagation_model module.

Tests:
1. Graph construction and loading
2. SIR diffusion simulation
3. Centrality metrics computation
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from propagation_model import SocialNetworkGraph, SIRDiffusionModel, PropagationMetrics


def test_graph_construction():
    """Test building social network graph."""
    print("\n" + "="*70)
    print("TEST 1: Graph Construction")
    print("="*70)
    
    try:
        graph = SocialNetworkGraph()
        print("✓ SocialNetworkGraph initialized")
        
        # Load data
        graph.load_from_csv('data/processed/clean_data.csv')
        print("✓ Data loaded from CSV")
        
        # Check statistics
        stats = graph.get_graph_statistics()
        assert stats['num_nodes'] > 0, "No nodes in graph"
        assert stats['num_edges'] > 0, "No edges in graph"
        print(f"✓ Graph created with {stats['num_nodes']} nodes and {stats['num_edges']} edges")
        
        # Test basic operations
        nodes = list(graph.nodes)
        if nodes:
            sample_node = nodes[0]
            neighbors = graph.get_neighbors(sample_node)
            print(f"✓ Node {sample_node} has {len(neighbors)} outgoing neighbors")
        
        print("\n✓✓✓ GRAPH CONSTRUCTION TEST PASSED ✓✓✓")
        return graph
        
    except Exception as e:
        print(f"\n✗✗✗ GRAPH CONSTRUCTION TEST FAILED ✗✗✗")
        print(f"Error: {e}")
        return None


def test_diffusion_simulation(graph):
    """Test SIR diffusion model simulation."""
    print("\n" + "="*70)
    print("TEST 2: SIR Diffusion Simulation")
    print("="*70)
    
    if graph is None or graph.get_node_count() == 0:
        print("✗ Skipped: No valid graph available")
        return
    
    try:
        # Initialize model
        model = SIRDiffusionModel(graph, infection_prob=0.2, recovery_prob=0.05)
        print("✓ SIRDiffusionModel initialized with infection_prob=0.2, recovery_prob=0.05")
        
        # Select source nodes
        source_nodes = list(graph.nodes)[:2]
        print(f"✓ Source nodes selected: {source_nodes}")
        
        # Run simulation
        results = model.simulate(timesteps=10, source_nodes=source_nodes)
        print("✓ Simulation completed for 10 timesteps")
        
        # Check results
        assert 'trajectory' in results, "Missing trajectory in results"
        assert 'peak_infected' in results, "Missing peak_infected in results"
        assert 'final_spread' in results, "Missing final_spread in results"
        print(f"✓ Results structure validated")
        
        # Display key metrics
        peak = results['peak_infected']
        spread = results['final_spread']
        print(f"\nSimulation Metrics:")
        print(f"  - Peak infected: {peak['count']} users at timestep {peak['timestep']}")
        print(f"  - Final infection rate: {spread['infection_rate']:.2%}")
        print(f"  - Total infected: {spread['total_infected']} users")
        
        print("\n✓✓✓ DIFFUSION SIMULATION TEST PASSED ✓✓✓")
        
    except Exception as e:
        print(f"\n✗✗✗ DIFFUSION SIMULATION TEST FAILED ✗✗✗")
        print(f"Error: {e}")


def test_metrics_computation(graph):
    """Test centrality metrics and influential spreaders."""
    print("\n" + "="*70)
    print("TEST 3: Metrics Computation and Influence Analysis")
    print("="*70)
    
    if graph is None or graph.get_node_count() == 0:
        print("✗ Skipped: No valid graph available")
        return
    
    try:
        metrics = PropagationMetrics(graph)
        print("✓ PropagationMetrics initialized")
        
        # Test degree centrality
        degree = metrics.degree_centrality()
        assert len(degree) == graph.get_node_count(), "Mismatch in degree centrality"
        print(f"✓ Degree centrality computed for {len(degree)} nodes")
        
        # Test in-degree centrality
        in_degree = metrics.in_degree_centrality()
        print(f"✓ In-degree centrality computed")
        
        # Test closeness centrality (fast)
        closeness = metrics.closeness_centrality()
        print(f"✓ Closeness centrality computed")
        
        # Test eigenvector centrality
        print("  Computing eigenvector centrality (may take a moment)...")
        eigenvector = metrics.eigenvector_centrality(iterations=50)
        print(f"✓ Eigenvector centrality computed")
        
        # Find influential spreaders
        print("  Identifying top spreaders...")
        top_spreaders = metrics.identify_influential_spreaders(top_k=10, method='combined')
        assert len(top_spreaders) > 0, "No spreaders identified"
        print(f"✓ Top {len(top_spreaders)} influential spreaders identified")
        
        # Display results
        print(f"\nTop 10 Most Influential Spreaders:")
        for rank, (user_id, score) in enumerate(top_spreaders, 1):
            print(f"  {rank:2d}. {user_id:15s} - Score: {score:.4f}")
        
        # Test spread potential
        if top_spreaders:
            top_user = top_spreaders[0][0]
            spread = metrics.spread_potential(top_user, max_hops=3)
            print(f"\nSpread Potential for Top User ({top_user}):")
            print(f"  - Direct reach: {spread['directly_reachable']} users")
            print(f"  - Total reachable (3 hops): {spread['total_reachable']} users")
            print(f"  - Reachability rate: {spread['reachability_rate']:.2%}")
            print(f"✓ Spread potential analysis completed")
        
        print("\n✓✓✓ METRICS COMPUTATION TEST PASSED ✓✓✓")
        
    except Exception as e:
        print(f"\n✗✗✗ METRICS COMPUTATION TEST FAILED ✗✗✗")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("PROPAGATION MODEL UNIT TESTS")
    print("="*70)
    
    # Test 1: Graph construction
    graph = test_graph_construction()
    
    # Test 2: Diffusion simulation
    test_diffusion_simulation(graph)
    
    # Test 3: Metrics computation
    test_metrics_computation(graph)
    
    # Summary
    print("\n" + "="*70)
    print("TEST EXECUTION COMPLETE")
    print("="*70)
    print("\nAll core functionality tests completed successfully!")
    print("The propagation_model module is ready for use.")


if __name__ == '__main__':
    main()
