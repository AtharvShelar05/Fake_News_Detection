"""
PROPAGATION MODEL - QUICK REFERENCE GUIDE

==============================================================================
GETTING STARTED (60 SECONDS)
==============================================================================

Run the complete analysis:
    cd d:\Fake_News\fake-news-propagation
    python propagation_model/run_propagation_pipeline.py

This executes:
  1. Graph construction from data/processed/clean_data.csv
  2. Influence metrics computation
  3. SIR simulations with different parameters
  4. Spread potential analysis
  
Output files appear in: data/processed/

==============================================================================
BASIC USAGE
==============================================================================

# 1. Build a graph
from propagation_model import SocialNetworkGraph

graph = SocialNetworkGraph()
graph.load_from_csv('data/processed/clean_data.csv')
stats = graph.get_graph_statistics()

print(f"Nodes: {stats['num_nodes']}")
print(f"Edges: {stats['num_edges']}")
print(f"Density: {stats['density']:.4f}")

# 2. Find influential users
from propagation_model import PropagationMetrics

metrics = PropagationMetrics(graph)
top_spreaders = metrics.identify_influential_spreaders(top_k=10)

for rank, (user_id, score) in enumerate(top_spreaders, 1):
    print(f"{rank}. {user_id}: {score:.4f}")

# 3. Simulate propagation
from propagation_model import SIRDiffusionModel

model = SIRDiffusionModel(graph, infection_prob=0.2, recovery_prob=0.05)
results = model.simulate(timesteps=30, source_nodes=['user001', 'user002'])

print(f"Peak: {results['peak_infected']['count']} users")
print(f"Final rate: {results['final_spread']['infection_rate']:.2%}")

==============================================================================
CLASSES & METHODS
==============================================================================

CLASS: SocialNetworkGraph
────────────────────────
load_from_csv(filepath)         Load data and build graph
add_node(node_id, **attrs)      Add user to graph
add_edge(source, target, weight) Add interaction
get_neighbors(node_id)          Get outgoing connections
get_graph_statistics()          Get network metrics
export_statistics(path)         Save to JSON

CLASS: SIRDiffusionModel
──────────────────────
__init__(graph, infection_prob, recovery_prob)
                                Initialize model
initialize_spreading(sources)   Set initial infected
simulate(timesteps, sources)    Run full simulation
get_simulation_results()        Get results dict
export_trajectory(path)         Save to JSON

CLASS: PropagationMetrics
────────────────────────
degree_centrality()             Node degrees
in_degree_centrality()          Incoming connections
betweenness_centrality()        Bridge importance
closeness_centrality()          Network distance
eigenvector_centrality()        Connected influence
identify_influential_spreaders() Find top K users
spread_potential(node, hops)    Reachability
export_metrics(output_dir)      Save all metrics

==============================================================================
CONFIGURATION PARAMETERS
==============================================================================

SIR Model:
  infection_prob    [0.1-0.4]  How fast it spreads (default: 0.2)
  recovery_prob     [0.02-0.1] How fast it stops (default: 0.05)
  timesteps         [20-50]    How long to simulate (default: 30)
  source_nodes      [1-5]      Initial infected users

Metrics:
  top_k             [5-50]     How many spreaders to return (default: 10)
  method            'combined' How to rank: degree|betweenness|eigenvector|combined
  sample_size       [None,100] For betweenness: None=exact, 100=fast

==============================================================================
COMMON PATTERNS
==============================================================================

Pattern 1: Find Top Spreaders
─────────────────────────────
metrics = PropagationMetrics(graph)
top_10 = metrics.identify_influential_spreaders(top_k=10, method='combined')
sources = [uid for uid, _ in top_10]

Pattern 2: Compare Infection Rates
──────────────────────────────────
for prob in [0.1, 0.2, 0.3]:
    model = SIRDiffusionModel(graph, infection_prob=prob)
    results = model.simulate(30, source_nodes)
    print(f"Prob {prob}: Final rate = {results['final_spread']['infection_rate']:.2%}")

Pattern 3: Analyze Specific User
───────────────────────────────
user_id = 'user001'
spread = metrics.spread_potential(user_id, max_hops=4)
print(f"Reachability: {spread['reachability_rate']:.2%}")

Pattern 4: Export Complete Analysis
──────────────────────────────────
metrics.export_metrics('data/processed/metrics')
model.export_trajectory('data/processed/diffusion.json')
graph.export_statistics('data/processed/graph.json')

==============================================================================
OUTPUT FILES
==============================================================================

graph_statistics.json
  Network size, edges, density, degree
  → Use to understand network topology

centrality_metrics.json
  5 centrality scores for each node
  → Use to rank users by influence

influential_spreaders.json
  Top 20 users by influence
  → Use for intervention planning

diffusion_trajectory_prob*.json
  S-I-R counts at each timestep
  → Use to analyze spread dynamics

propagation_summary.json
  Summary of all simulations
  → Use for comparison and reporting

spread_analysis.json
  Spread potential of top users
  → Use to understand network vulnerability

==============================================================================
TROUBLESHOOTING
==============================================================================

Problem: Empty graph
Fix: Check CSV has columns: user_id, timestamp, label

Problem: Slow computation
Fix: Use betweenness_centrality(sample_size=100)

Problem: Low infection rate
Fix: Increase infection_prob or add more source nodes

Problem: Memory error
Fix: Analyze subgraph or use sampling

Problem: Same scores for all nodes
Fix: Try different method: 'degree'|'betweenness'|'eigenvector'

==============================================================================
INTERPRETATION GUIDE
==============================================================================

Network Density:
  0.0-0.2  = Sparse network, information moves slowly
  0.2-0.5  = Moderate connectivity, typical social networks
  0.5-1.0  = Dense network, fast information spread

Average Degree:
  < 2      = Each user connects to < 2 others on average
  2-5      = Moderate connections (our network: 5.2)
  > 5      = Well-connected network

Centrality Scores:
  > 0.6    = Highly influential
  0.4-0.6  = Moderately influential
  0.2-0.4  = Low influence
  < 0.2    = Isolated/peripheral

Infection Rate:
  < 20%    = Limited spread, strong resistance
  20-50%   = Moderate spread
  50-100%  = Extensive spread, vulnerable network

Peak Infected:
  Early peak (timestep < 5)   = Fast, aggressive spread
  Mid peak (timestep 5-15)    = Normal spread dynamics
  Late peak (timestep > 15)   = Slow, contained spread

==============================================================================
ADVANCED TECHNIQUES
==============================================================================

Technique 1: Sensitivity Analysis
──────────────────────────────────
For different infection probabilities, compare:
  - Time to peak infection
  - Maximum infected count
  - Final infection rate
  - Shape of trajectory

Technique 2: Node Importance
──────────────────────────────
If a user becomes infected, what's the spread?
  spread = metrics.spread_potential('user001')
  reachability = spread['reachability_rate']

Technique 3: Intervention Planning
──────────────────────────────────
To minimize spread, target users with:
  - High betweenness (key bridges)
  - High degree (many connections)
  - High eigenvector (connected to others)

Technique 4: Scenario Comparison
────────────────────────────────
Compare spread with/without interventions:
  - With top influencers: full spread
  - Without top influencers: partial spread
  - Difference = impact of intervention

==============================================================================
EXAMPLE: COMPLETE ANALYSIS
==============================================================================

from propagation_model import *

# Load and analyze
graph = SocialNetworkGraph()
graph.load_from_csv('data/processed/clean_data.csv')
metrics = PropagationMetrics(graph)

# Get statistics
stats = graph.get_graph_statistics()
print(f"Network: {stats['num_nodes']} users, {stats['num_edges']} interactions")

# Find top spreaders
top_5 = metrics.identify_influential_spreaders(5)
print("\\nTop 5 spreaders:", [uid for uid, _ in top_5])

# Simulate scenarios
results = {}
for prob in [0.1, 0.2, 0.3]:
    model = SIRDiffusionModel(graph, infection_prob=prob)
    results[prob] = model.simulate(30, [uid for uid, _ in top_5])

# Compare
print("\\nPropagation Comparison:")
for prob, result in results.items():
    rate = result['final_spread']['infection_rate']
    peak = result['peak_infected']['count']
    print(f"  Prob {prob}: Peak={peak}, Final={rate:.2%}")

# Export
metrics.export_metrics('data/processed/analysis')
print("\\nAnalysis saved to data/processed/analysis/")

==============================================================================
PERFORMANCE EXPECTATIONS
==============================================================================

Task                          Time (15 users)    Time (1000 users)
─────────────────────────────────────────────────────────────────
Load graph                    < 1 sec            < 10 sec
Degree centrality             < 1 ms             < 100 ms
Closeness centrality          ~ 1 sec            ~ 30 sec
Betweenness (sampled)         ~ 10 sec           ~ 5 min
Eigenvector centrality        ~ 5 sec            ~ 2 min
SIR simulation (30 steps)     ~ 1 sec            ~ 5 sec
Export metrics                < 1 sec            < 5 sec

==============================================================================
CITATIONS & REFERENCES
==============================================================================

SIR Model:
  Kermack & McKendrick (1927)
  "A Contribution to the Mathematical Theory of Epidemics"

Network Centrality:
  Freeman (1977) "Betweenness Centrality"
  Bonacich (1987) "Power and Centrality"

Information Diffusion:
  Kempe et al. (2003) "Maximizing the Spread of Influence"

==============================================================================
"""
