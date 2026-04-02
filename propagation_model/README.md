# Misinformation Propagation Modeling Module

## Overview

The `propagation_model` module provides a complete framework for modeling how fake news and misinformation spread through social networks. It combines graph theory, epidemic dynamics, and network science to analyze and simulate information propagation patterns.

**Project:** Large-Scale Fake News Propagation Modeling Under Adversarial Content Evolution

---

## Module Architecture

### Three Core Components

#### 1. **build_graph.py** - Social Network Construction
Constructs directed, weighted graphs representing user interactions in social networks.

- **Class:** `SocialNetworkGraph`
- **Key Features:**
  - Load social media data from CSV files
  - Create nodes (users) and edges (interactions)
  - Support weighted edges for interaction strength
  - Compute graph statistics and topology metrics

**Example:**
```python
from propagation_model import SocialNetworkGraph

graph = SocialNetworkGraph()
graph.load_from_csv('data/processed/clean_data.csv')
stats = graph.get_graph_statistics()
```

#### 2. **diffusion_model.py** - SIR Propagation Simulation
Implements epidemic-inspired SIR (Susceptible-Infected-Recovered) diffusion model to simulate news spread.

- **Class:** `SIRDiffusionModel`
- **Key Features:**
  - S→I→R state transitions for users
  - Configurable infection and recovery probabilities
  - Timestep-by-timestep simulation
  - Track infection trajectories and peak metrics

**Example:**
```python
from propagation_model import SIRDiffusionModel

model = SIRDiffusionModel(graph, infection_prob=0.2, recovery_prob=0.05)
results = model.simulate(timesteps=30, source_nodes=['user001', 'user002'])
```

#### 3. **metrics.py** - Network Analysis & Influence
Computes centrality measures and identifies influential spreaders.

- **Class:** `PropagationMetrics`
- **Key Features:**
  - 5 centrality measures (degree, in-degree, betweenness, closeness, eigenvector)
  - Identify top influential spreaders
  - Analyze spread potential of nodes
  - Export comprehensive metrics

**Example:**
```python
from propagation_model import PropagationMetrics

metrics = PropagationMetrics(graph)
top_spreaders = metrics.identify_influential_spreaders(top_k=20, method='combined')
```

---

## Quick Start

### Installation

Ensure required dependencies are installed:
```bash
pip install pandas numpy
```

### Basic Usage

Run the complete pipeline:
```bash
python propagation_model/run_propagation_pipeline.py
```

This executes all four analysis steps:
1. **Graph Construction** - Load data and build network
2. **Metrics Computation** - Calculate influence scores
3. **Propagation Simulation** - Run SIR model with different parameters
4. **Spread Analysis** - Evaluate reachability of top influencers

### Quick Example

```python
# Import modules
from propagation_model import SocialNetworkGraph, SIRDiffusionModel, PropagationMetrics

# Build graph
graph = SocialNetworkGraph()
graph.load_from_csv('data/processed/clean_data.csv')

# Find influential users
metrics = PropagationMetrics(graph)
top_10 = metrics.identify_influential_spreaders(top_k=10)

# Simulate spread
model = SIRDiffusionModel(graph, infection_prob=0.2)
results = model.simulate(timesteps=30, source_nodes=[uid for uid, _ in top_10[:3]])

# View results
print(f"Peak infected: {results['peak_infected']['count']}")
print(f"Final infection rate: {results['final_spread']['infection_rate']:.2%}")
```

---

## Component Details

### Graph Construction (`build_graph.py`)

#### SocialNetworkGraph Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `load_from_csv(path)` | Load user interaction data | None |
| `add_node(node_id, **attrs)` | Add user to graph | None |
| `add_edge(source, target, weight)` | Add interaction | None |
| `get_neighbors(node_id)` | Get outgoing connections | Dict[str, int] |
| `get_in_neighbors(node_id)` | Get incoming connections | Dict[str, int] |
| `get_graph_statistics()` | Compute topology metrics | Dict |
| `export_statistics(path)` | Save stats to JSON | None |

#### Data Format

Expected CSV columns:
- `user_id`: Unique user identifier
- `timestamp`: When content was posted
- `text` or `clean_text`: Content
- `label`: 0 = legitimate, 1 = fake news

---

### SIR Diffusion Model (`diffusion_model.py`)

#### SIRDiffusionModel Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `__init__(graph, infection_prob, recovery_prob)` | Initialize model | SIRDiffusionModel |
| `initialize_spreading(source_nodes)` | Set initial infected | None |
| `simulate_step(timestep)` | Simulate one timestep | Tuple[int, int, int] |
| `simulate(timesteps, source_nodes)` | Full simulation | Dict |
| `get_simulation_results()` | Get results | Dict |
| `get_trajectory()` | Get S-I-R over time | List[Tuple] |
| `export_trajectory(path)` | Save to JSON | None |

#### Key Parameters

- **infection_prob** (0-1): Probability of infection per timestep
  - Higher = faster spread
  - Typical range: 0.1-0.4

- **recovery_prob** (0-1): Probability of recovery per timestep
  - Higher = shorter infection duration
  - Typical range: 0.02-0.1

- **timesteps**: Number of simulation steps (e.g., 20-50)

- **source_nodes**: Initial infected users (e.g., 1-5 nodes)

#### Output Structure

```json
{
  "trajectory": [[S, I, R], ...],
  "peak_infected": {"count": 15, "timestep": 6},
  "final_spread": {
    "total_infected": 15,
    "infection_rate": 1.0
  },
  "statistics": {
    "total_timesteps": 30,
    "total_users": 15,
    "source_nodes": 3
  }
}
```

---

### Centrality Metrics (`metrics.py`)

#### Available Centrality Measures

1. **Degree Centrality**
   - Direct connections from a node
   - Fast, local measure
   - Range: [0, 1]

2. **In-Degree Centrality**
   - Incoming connections
   - Measures exposure/reach
   - Range: [0, 1]

3. **Betweenness Centrality**
   - Importance as network bridge
   - Identifies key connectors
   - Range: [0, 1]

4. **Closeness Centrality**
   - Average distance to other nodes
   - Central hub identification
   - Range: [0, 1]

5. **Eigenvector Centrality**
   - Influence through connections
   - Connected to important nodes
   - Range: [0, 1]

#### PropagationMetrics Methods

| Method | Description | Returns |
|--------|-------------|---------|
| `degree_centrality()` | Compute degree scores | Dict |
| `in_degree_centrality()` | Compute in-degree scores | Dict |
| `betweenness_centrality(sample_size)` | Compute betweenness | Dict |
| `closeness_centrality()` | Compute closeness | Dict |
| `eigenvector_centrality(iterations)` | Compute eigenvector | Dict |
| `identify_influential_spreaders(top_k, method)` | Top K spreaders | List[Tuple] |
| `spread_potential(source_node, hops)` | Reachability analysis | Dict |
| `export_metrics(output_dir)` | Save all metrics | None |

#### Methods for Ranking

- **'degree'**: Most direct connections
- **'betweenness'**: Most important bridges
- **'eigenvector'**: Connected to influential nodes
- **'combined'**: Weighted combination of all (default, recommended)

---

## Output Files

The pipeline generates the following outputs in `data/processed/`:

| File | Description |
|------|-------------|
| `graph_statistics.json` | Network topology metrics |
| `centrality_metrics.json` | All 5 centrality measures per node |
| `influential_spreaders.json` | Top 20 users by combined influence |
| `diffusion_trajectory_prob*.json` | S-I-R curves for each infection probability |
| `propagation_summary.json` | Summary of all simulations |
| `spread_analysis.json` | Spread potential of top 5 influencers |

---

## Configuration & Customization

### Adjusting Infection Parameters

```python
# High infection rate (aggressive spread)
model = SIRDiffusionModel(graph, infection_prob=0.4, recovery_prob=0.02)

# Low infection rate (conservative spread)
model = SIRDiffusionModel(graph, infection_prob=0.1, recovery_prob=0.1)

# Balanced scenario
model = SIRDiffusionModel(graph, infection_prob=0.2, recovery_prob=0.05)
```

### Selecting Source Nodes

```python
# From top influencers
top_spreaders = metrics.identify_influential_spreaders(top_k=5)
sources = [uid for uid, _ in top_spreaders]

# Random selection
import random
sources = random.sample(list(graph.nodes), k=3)

# Specific nodes
sources = ['user001', 'user002', 'user003']
```

### Adjusting Metrics Parameters

```python
# Fast betweenness (for large graphs)
betweenness = metrics.betweenness_centrality(sample_size=100)

# Precise betweenness (slower)
betweenness = metrics.betweenness_centrality(sample_size=None)

# More iterations for eigenvector
eigenvector = metrics.eigenvector_centrality(iterations=200)
```

---

## Performance Considerations

### Computational Complexity

| Operation | Complexity | Time (N=1000) |
|-----------|-----------|---------------|
| Graph Load | O(edges) | <1s |
| Degree Centrality | O(n) | <1ms |
| Closeness | O(n²) | ~1s |
| Betweenness (sampled) | O(s·n²) | ~10s |
| Eigenvector (i iterations) | O(i·n²) | ~5s |
| SIR Simulation (t steps) | O(t·edges) | ~1s |

### Memory Requirements

- Graph: O(n + edges)
- Metrics: O(n)
- Simulation: O(n)

### Optimization Tips

1. **For large graphs (>10K users):**
   - Use betweenness sampling: `betweenness_centrality(sample_size=100)`
   - Reduce eigenvector iterations: `eigenvector_centrality(iterations=50)`

2. **For fast results:**
   - Use only degree centrality
   - Run simulations with fewer timesteps
   - Reduce number of metrics computed

3. **For accurate results:**
   - Use full betweenness (no sampling)
   - Increase eigenvector iterations to 200+
   - Run multiple simulations with different seeds

---

## Use Cases

### 1. Misinformation Spread Analysis
Understand how fake news propagates and identify critical spreaders:
```python
# Find key influencers
influential = metrics.identify_influential_spreaders(top_k=50)

# Simulate their impact
model = SIRDiffusionModel(graph, infection_prob=0.25)
results = model.simulate(30, [uid for uid, _ in influential[:5]])
```

### 2. Intervention Strategy Evaluation
Test effectiveness of targeting specific users:
```python
# Scenario 1: Target top influencers
model1 = SIRDiffusionModel(graph, infection_prob=0.2)
results1 = model1.simulate(30, top_influencers)

# Scenario 2: Target bridge connectors
betweenness = metrics.betweenness_centrality()
bridges = sorted(betweenness.items(), key=lambda x: -x[1])[:5]
model2 = SIRDiffusionModel(graph, infection_prob=0.2)
results2 = model2.simulate(30, [uid for uid, _ in bridges])
```

### 3. Network Resilience Assessment
Evaluate network vulnerability to misinformation:
```python
# Test different infection rates
for prob in [0.05, 0.15, 0.25, 0.35]:
    model = SIRDiffusionModel(graph, infection_prob=prob)
    results = model.simulate(30, source_nodes)
    rate = results['final_spread']['infection_rate']
    print(f"Infection prob {prob}: {rate:.2%} reach")
```

### 4. Dynamics Comparison
Compare spread under different network conditions:
```python
# With/without targeted users
sources_random = random.sample(list(graph.nodes), 3)
sources_strategic = [uid for uid, _ in influential[:3]]

for name, sources in [("Random", sources_random), ("Strategic", sources_strategic)]:
    model = SIRDiffusionModel(graph, infection_prob=0.2)
    results = model.simulate(30, sources)
    print(f"{name}: {results['peak_infected']['count']} peak infected")
```

---

## Testing

Run the test suite:
```bash
python propagation_model/test_module.py
```

Tests cover:
- Graph construction and loading
- SIR simulation with multiple timesteps
- Centrality computation
- Influential spreader identification
- Spread potential analysis

---

## Troubleshooting

### Issue: Empty graph after loading
**Solution:** Verify CSV has required columns (`user_id`, `timestamp`, `label`)

### Issue: Very slow metric computation
**Solution:** Use sampling for betweenness:
```python
metrics.betweenness_centrality(sample_size=100)
```

### Issue: Low infection rates in SIR
**Solution:** Increase `infection_prob` or use more source nodes:
```python
model = SIRDiffusionModel(graph, infection_prob=0.3)
results = model.simulate(30, source_nodes[:5])
```

### Issue: Memory errors
**Solution:** Use subgraph analysis or increase sampling rate

---

## API Reference

### SocialNetworkGraph

```python
class SocialNetworkGraph:
    def load_from_csv(filepath: str) -> None
    def add_node(node_id: str, **attributes) -> None
    def add_edge(source: str, target: str, weight: int = 1) -> None
    def get_neighbors(node_id: str) -> Dict[str, int]
    def get_in_neighbors(node_id: str) -> Dict[str, int]
    def get_node_count() -> int
    def get_edge_count() -> int
    def get_total_weight() -> int
    def get_graph_statistics() -> Dict
    def to_adjacency_dict() -> Dict
    def export_statistics(output_path: str = None) -> Dict
```

### SIRDiffusionModel

```python
class SIRDiffusionModel:
    def __init__(graph, infection_prob: float = 0.3, recovery_prob: float = 0.1)
    def initialize_spreading(source_nodes: List[str]) -> None
    def simulate_step(timestep: int) -> Tuple[int, int, int]
    def simulate(timesteps: int, source_nodes: List[str]) -> Dict
    def get_simulation_results() -> Dict
    def get_trajectory() -> List[Tuple[int, int, int]]
    def get_infected_by_node() -> Dict[str, int]
    def export_trajectory(output_path: str) -> None
```

### PropagationMetrics

```python
class PropagationMetrics:
    def __init__(graph)
    def degree_centrality() -> Dict[str, float]
    def in_degree_centrality() -> Dict[str, float]
    def betweenness_centrality(sample_size: int = None) -> Dict[str, float]
    def closeness_centrality() -> Dict[str, float]
    def eigenvector_centrality(iterations: int = 100) -> Dict[str, float]
    def spread_potential(source_node: str, max_hops: int = 3) -> Dict
    def identify_influential_spreaders(top_k: int = 10, method: str = 'combined') -> List[Tuple[str, float]]
    def export_metrics(output_dir: str) -> None
```

---

## References

**SIR Model:**
- Kermack, W. O., & McKendrick, A. G. (1927). "A Contribution to the Mathematical Theory of Epidemics"

**Network Centrality:**
- Freeman, L. C. (1977). "A set of measures of centrality based on betweenness"
- Bonacich, P. (1987). "Power and centrality"

**Information Diffusion:**
- Kempe, D., Kleinberg, J., & Tardos, É. (2003). "Maximizing the spread of influence through a social network"

---

## License & Attribution

Part of: "Large-Scale Fake News Propagation Modeling Under Adversarial Content Evolution"

---

## Support

For issues, questions, or suggestions, refer to the documentation file: `PROPAGATION_DOCUMENTATION.md`
