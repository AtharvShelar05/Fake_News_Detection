"""
PROPAGATION MODEL MODULE DOCUMENTATION

Module Overview
===============
The propagation_model module implements a complete framework for modeling how
misinformation spreads through social networks. It combines graph theory,
epidemic dynamics, and network science to analyze and simulate fake news
propagation patterns.

Core Components
===============

1. BUILD_GRAPH.PY - Social Network Construction
   ============================================
   
   Class: SocialNetworkGraph
   
   Purpose:
     - Load social media interaction data
     - Construct directed, weighted graphs where:
       * Nodes = Users
       * Edges = Interactions (retweets, shares, replies)
       * Weights = Interaction frequency/strength
   
   Key Methods:
     - load_from_csv(filepath): Load data and build graph
     - add_node(node_id, **attributes): Add user to graph
     - add_edge(source, target, weight): Add interaction
     - get_neighbors(node_id): Get outgoing connections
     - get_in_neighbors(node_id): Get incoming connections
     - get_graph_statistics(): Compute basic stats
     - export_statistics(output_path): Save stats to JSON
   
   Data Format Expected:
     CSV with columns: user_id, timestamp, text/clean_text, label
     label: 0 = legitimate, 1 = fake news
   
   Example Usage:
     ```python
     from propagation_model import SocialNetworkGraph
     
     graph = SocialNetworkGraph()
     graph.load_from_csv('data/processed/clean_data.csv')
     stats = graph.get_graph_statistics()
     ```
   
   Output Statistics:
     - num_nodes: Total users
     - num_edges: Total interactions
     - total_weight: Sum of interaction weights
     - avg_degree: Average connections per user
     - density: Network connectivity ratio


2. DIFFUSION_MODEL.PY - SIR Propagation Simulation
   ==============================================
   
   Class: SIRDiffusionModel
   
   Purpose:
     - Simulate fake news spread using SIR epidemic model
     - Susceptible (S) → Infected (I) → Recovered (R) dynamics
     - Model temporal spread with configurable parameters
   
   States:
     - Susceptible (S): Haven't seen the fake news
     - Infected (I): Actively spreading the misinformation
     - Recovered (R): Stopped spreading (became skeptical)
   
   Key Methods:
     - __init__(graph, infection_prob, recovery_prob): Initialize model
     - initialize_spreading(source_nodes): Set initial infected users
     - simulate_step(timestep): Simulate one time unit
     - simulate(timesteps, source_nodes): Run full simulation
     - get_simulation_results(): Get trajectory and statistics
     - get_infected_by_node(): Map each user to infection time
     - export_trajectory(output_path): Save results to JSON
   
   Parameters:
     - infection_prob (0-1): Per-timestep infection transmission probability
     - recovery_prob (0-1): Per-timestep recovery (skepticism) probability
     - timesteps: Number of simulation steps
     - source_nodes: Initial spreaders
   
   Example Usage:
     ```python
     from propagation_model import SIRDiffusionModel
     
     model = SIRDiffusionModel(
         graph,
         infection_prob=0.2,
         recovery_prob=0.05
     )
     results = model.simulate(
         timesteps=30,
         source_nodes=['user001', 'user002']
     )
     
     print(f"Peak infected: {results['peak_infected']['count']}")
     print(f"Final infection rate: {results['final_spread']['infection_rate']:.2%}")
     ```
   
   Output Trajectory:
     - For each timestep: (susceptible_count, infected_count, recovered_count)
     - Peak infection metrics
     - Final spread statistics
     - Infection times for each node


3. METRICS.PY - Network and Influence Analysis
   ==========================================
   
   Class: PropagationMetrics
   
   Purpose:
     - Compute network centrality measures
     - Identify influential spreaders
     - Analyze spread potential
   
   Centrality Measures:
   
     a) Degree Centrality
        - Counts direct connections
        - Formula: degree / (n-1)
        - Fast computation, local measure
        - High degree = many direct contacts
     
     b) In-Degree Centrality
        - Counts incoming connections
        - Formula: in_degree / (n-1)
        - Measures exposure/reach
     
     c) Betweenness Centrality
        - Importance as bridge in network
        - Formula: sum(shortest paths through node)
        - Slow but identifies key connectors
        - Can use sampling for large graphs
     
     d) Closeness Centrality
        - Average distance to other nodes
        - Formula: (n-1) / sum(distances)
        - Identifies central hubs
     
     e) Eigenvector Centrality
        - Influence through influential connections
        - Formula: x = A*x (power iteration)
        - Identifies nodes connected to important nodes
     
   Key Methods:
     - degree_centrality(): Get node degree scores
     - in_degree_centrality(): Get in-degree scores
     - betweenness_centrality(sample_size): Bridge importance
     - closeness_centrality(): Network distance
     - eigenvector_centrality(iterations): Connected importance
     - spread_potential(source_node, max_hops): Reachability
     - identify_influential_spreaders(top_k, method): Get top spreaders
     - export_metrics(output_dir): Save all metrics
   
   Methods for Finding Top Spreaders:
     - 'degree': Highest direct connections
     - 'betweenness': Most important bridges
     - 'eigenvector': Connected to influential nodes
     - 'combined': Weighted combination of all (DEFAULT)
   
   Example Usage:
     ```python
     from propagation_model import PropagationMetrics
     
     metrics = PropagationMetrics(graph)
     
     # Find top spreaders
     top_spreaders = metrics.identify_influential_spreaders(
         top_k=20,
         method='combined'
     )
     
     # Analyze specific user
     spread = metrics.spread_potential('user001', max_hops=3)
     print(f"Reachable in 3 hops: {spread['total_reachable']}")
     
     # Export all metrics
     metrics.export_metrics('data/processed/metrics')
     ```


Integration Pipeline
====================

run_propagation_pipeline.py provides end-to-end execution:

Step 1: Build Graph
   - Load clean_data.csv
   - Create user nodes and interaction edges
   - Export graph statistics

Step 2: Compute Metrics
   - Calculate all centrality measures
   - Identify top 20 influential spreaders
   - Export metrics to JSON files

Step 3: Simulate Propagation
   - Run SIR model with multiple infection probabilities
   - Compare spread dynamics
   - Export trajectory files

Step 4: Analyze Spread Potential
   - Evaluate reachability of top influencers
   - Compute spread statistics
   - Export analysis results

Example Execution:
   python propagation_model/run_propagation_pipeline.py


Configuration Parameters
========================

Graph Construction:
   - Data source: data/processed/clean_data.csv
   - Interaction inference: Shared content temporal flow

SIR Model:
   - infection_prob: [0.1, 0.2, 0.3] (tested values)
   - recovery_prob: 0.05 (default, can be adjusted)
   - timesteps: 30 (simulation duration)

Metrics:
   - betweenness_sample_size: 100 (for large graphs)
   - eigenvector_iterations: 100 (convergence steps)
   - spread_potential_hops: 3-4 (neighborhood depth)


Output Files Generated
======================

1. graph_statistics.json
   - Network topology metrics
   - Number of nodes, edges, weights
   - Density and average degree

2. centrality_metrics.json
   - All five centrality measures for each node
   - Normalized scores [0, 1]

3. influential_spreaders.json
   - Top 20 users by combined influence
   - User ID and influence score

4. diffusion_trajectory_prob*.json
   - S-I-R counts at each timestep
   - Peak infection information
   - Final spread statistics

5. propagation_summary.json
   - Overview of all simulations
   - Configuration parameters used
   - Comparison across infection probabilities

6. spread_analysis.json
   - Direct reach of top 5 influencers
   - Reachability statistics
   - Hop-based distribution


Performance Considerations
==========================

Graph Size Impact:
   - Nodes (users): O(n)
   - Edges (interactions): O(n²) worst case, O(n) typical
   - Memory: Adjacency list efficient for sparse graphs

Metric Computation Time:
   - Degree: O(n) - very fast
   - Closeness: O(n²) - moderate
   - Betweenness: O(n³) worst case, sampling reduces to O(s*n²)
   - Eigenvector: O(i*n²) where i = iterations

SIR Simulation:
   - Per timestep: O(edges * neighborhoods)
   - Linear with simulation duration
   - Early stopping when spread halts


Use Cases
=========

1. Misinformation Spread Analysis
   - Understand how fake news propagates
   - Identify critical spreaders
   - Compare scenarios

2. Intervention Planning
   - Target key influencers for fact-checking
   - Design counter-messaging strategies
   - Predict spread impact of interventions

3. Network Vulnerability Assessment
   - Identify critical nodes in network
   - Understand cascade patterns
   - Plan resilience improvements

4. Dynamics Comparison
   - Test different parameters
   - Compare infection rates
   - Evaluate recovery strategies


Code Examples
=============

Example 1: Simple Graph Analysis
   ```python
   from propagation_model import SocialNetworkGraph, PropagationMetrics
   
   # Build graph
   graph = SocialNetworkGraph()
   graph.load_from_csv('data/processed/clean_data.csv')
   
   # Analyze metrics
   metrics = PropagationMetrics(graph)
   top_10 = metrics.identify_influential_spreaders(top_k=10)
   
   for user_id, score in top_10:
       print(f"{user_id}: {score:.4f}")
   ```

Example 2: Single Simulation
   ```python
   from propagation_model import SIRDiffusionModel
   
   model = SIRDiffusionModel(graph, infection_prob=0.25)
   results = model.simulate(timesteps=20, source_nodes=['user001'])
   
   trajectory = results['trajectory']
   for t, (s, i, r) in enumerate(trajectory):
       print(f"t={t}: S={s}, I={i}, R={r}")
   ```

Example 3: Comparative Analysis
   ```python
   results = {}
   for prob in [0.15, 0.25, 0.35]:
       model = SIRDiffusionModel(graph, infection_prob=prob)
       results[prob] = model.simulate(20, ['user001', 'user002'])
       
       rate = results[prob]['final_spread']['infection_rate']
       print(f"prob={prob}: infection_rate={rate:.2%}")
   ```


Dependencies
============

Required:
   - pandas: Data loading and manipulation
   - numpy: Numerical computations
   - collections: Data structures (deque, defaultdict)
   - json: Output serialization

Optional (for visualization):
   - networkx: Extended graph algorithms
   - matplotlib: Plotting trajectories
   - seaborn: Statistical visualizations


Troubleshooting
===============

Issue: Empty graph after loading
   Solution: Verify CSV has required columns (user_id, timestamp, label)

Issue: Very slow betweenness computation
   Solution: Use sample_size parameter or reduce graph size

Issue: Low infection rates in SIR simulation
   Solution: Increase infection_prob or add more source nodes

Issue: Memory errors with large graphs
   Solution: Use sampling in metrics, consider subgraph analysis

Issue: Unexpected early termination
   Solution: Check recovery_prob isn't too high relative to infection_prob


References
==========

SIR Model:
   - Kermack, W. O., & McKendrick, A. G. (1927)
   - "A Contribution to the Mathematical Theory of Epidemics"
   - Extended to information diffusion in networks

Network Centrality:
   - Freeman, L. C. (1977) "A set of measures of centrality based on betweenness"
   - Bonacich, P. (1987) "Power and centrality"

Information Diffusion:
   - Kempe, D., Kleinberg, J., & Tardos, É. (2003)
   - "Maximizing the spread of influence through a social network"


Version History
===============

v1.0.0 (Current)
   - Initial implementation
   - SocialNetworkGraph for graph construction
   - SIRDiffusionModel for propagation simulation
   - PropagationMetrics for centrality analysis
   - Integration pipeline with multiple output formats
"""
