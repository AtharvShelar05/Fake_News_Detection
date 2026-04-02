# Visualization Module Documentation

## Overview

The Visualization Module provides comprehensive tools for analyzing and visualizing fake news propagation dynamics. It includes:

- **Network Visualization**: Graph structure analysis with centrality metrics
- **Diffusion Visualization**: SIR trajectory analysis across infection probability scenarios
- **Influence Visualization**: Influential spreader identification and ranking
- **Interactive Dashboard**: Streamlit-based web interface for exploratory analysis

## Installation

### Install Dependencies

```bash
pip install -r visualization/requirements.txt
```

### Required Packages
- matplotlib>=3.8.0
- networkx>=3.2
- plotly>=5.17.0
- streamlit>=1.28.0
- numpy>=1.24.0
- pandas>=2.1.0

## Components

### 1. Network Visualization (`network_visualization.py`)

Visualizes the social network topology with influence highlighting and centrality metrics.

#### Class: `NetworkVisualizer`

**Methods:**

- `load_data()`: Load graph statistics, centrality metrics, and influential spreaders data
- `build_graph()`: Construct NetworkX directed graph from loaded data
- `visualize_network()`: Spring layout visualization with node sizing by influence
- `visualize_network_interactive_html()`: Interactive Plotly version saved as HTML
- `visualize_centrality_comparison()`: 3-panel comparison (degree, in-degree, closeness)
- `generate_summary_report()`: Text report with network statistics

**Usage:**

```python
from visualization import NetworkVisualizer

viz = NetworkVisualizer()
viz.load_data()
viz.build_graph()
viz.visualize_network()  # Saves PNG
viz.visualize_network_interactive_html()  # Saves interactive HTML
report = viz.generate_summary_report()
print(report)
```

**Output Files:**
- `visualization/output/network_visualization.png`: Network graph
- `visualization/output/network_interactive.html`: Interactive version
- `visualization/output/centrality_comparison.png`: 3-panel centrality comparison
- `visualization/output/network_summary.txt`: Statistical summary

**Key Metrics:**
- Number of nodes and edges
- Network density
- Average degree
- Top 10 most central nodes by different metrics

---

### 2. Diffusion Visualization (`diffusion_visualization.py`)

Analyzes and visualizes SIR (Susceptible-Infected-Recovered) trajectories across different infection probability scenarios.

#### Class: `DiffusionVisualizer`

**Methods:**

- `load_trajectories()`: Load all diffusion trajectory files from data/processed/
- `parse_trajectory(trajectory_data)`: Extract S, I, R values from trajectory data
- `visualize_single_trajectory(probability)`: Plot SIR curve for specific probability
- `visualize_all_trajectories()`: Multi-panel comparison of all scenarios
- `visualize_peak_comparison()`: Analysis of peak infections, time-to-peak
- `generate_diffusion_summary()`: Comprehensive text analysis report

**Usage:**

```python
from visualization import DiffusionVisualizer

viz = DiffusionVisualizer()
viz.load_trajectories()

# Visualize specific scenario
viz.visualize_single_trajectory('0.1')  # 10% infection probability

# Compare all scenarios
viz.visualize_all_trajectories()

# Peak infection analysis
fig = viz.visualize_peak_comparison()

# Generate report
report = viz.generate_diffusion_summary()
```

**Output Files:**
- `visualization/output/trajectory_prob*.png`: Individual probability scenarios
- `visualization/output/trajectories_comparison.png`: Multi-panel comparison
- `visualization/output/peak_comparison.png`: Peak infection analysis
- `visualization/output/diffusion_summary.txt`: Statistical summary

**Key Metrics by Scenario:**
- Peak infected count
- Time to peak infection
- Final recovered count
- Spread rate (percentage)
- Total affected population

---

### 3. Influence Visualization (`influence_visualization.py`)

Identifies and analyzes the most influential spreaders in the network.

#### Class: `InfluenceVisualizer`

**Methods:**

- `load_data()`: Load influential spreaders and centrality metrics
- `visualize_top_spreaders(top_n=10)`: Horizontal bar chart of top spreaders
- `visualize_all_spreaders()`: Scatter plot showing rank vs influence
- `visualize_centrality_distributions()`: 3-panel histogram distributions
- `visualize_influence_vs_centrality()`: Correlation analysis across centrality types
- `generate_influence_report()`: Detailed text analysis

**Usage:**

```python
from visualization import InfluenceVisualizer

viz = InfluenceVisualizer()
viz.load_data()

# Top spreaders
viz.visualize_top_spreaders(top_n=15)  # Top 15 spreaders

# All spreaders distribution
viz.visualize_all_spreaders()

# Centrality distributions
viz.visualize_centrality_distributions()

# Correlation analysis
viz.visualize_influence_vs_centrality()

# Generate comprehensive report
report = viz.generate_influence_report()
```

**Output Files:**
- `visualization/output/top_spreaders.png`: Top N spreaders ranking
- `visualization/output/all_spreaders.png`: Scatter plot of all spreaders
- `visualization/output/centrality_distributions.png`: 3-panel distributions
- `visualization/output/influence_correlations.png`: Correlation heatmaps
- `visualization/output/influence_summary.txt`: Statistical detailed analysis

**Key Metrics:**
- Top 10 most influential spreaders
- Influence score distribution
- Correlation between centrality measures
- Network role classification

---

### 4. Interactive Dashboard (`dashboard.py`)

Streamlit-based interactive web application for exploratory analysis.

#### Pages:

1. **Overview**: Project statistics and dataset information
2. **Network Analysis**: Network topology with centrality measures
3. **Diffusion Dynamics**: SIR trajectories with scenario comparison
4. **Influence Analysis**: Spreader rankings with detailed statistics
5. **Comparative Analysis**: Cross-metric analysis and distributions

#### Usage:

```bash
# Run the dashboard
streamlit run visualization/dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

#### Features:

- **Interactive Selection**: Choose between infection probability scenarios
- **Dynamic Sliders**: Adjust number of top spreaders to display
- **Real-time Metrics**: Updated statistics based on selections
- **Responsive Layout**: Multi-column designs for comprehensive views
- **Data Tables**: Exportable spreader rankings and metrics

---

## Quick Start Guide

### Running All Visualizations

```bash
cd fake-news-propagation

# Install dependencies
pip install -r visualization/requirements.txt

# Run individual visualizers
python visualization/network_visualization.py
python visualization/diffusion_visualization.py
python visualization/influence_visualization.py

# Or launch interactive dashboard
streamlit run visualization/dashboard.py
```

### Output Directory Structure

```
visualization/
├── output/
│   ├── network_visualization.png
│   ├── network_interactive.html
│   ├── centrality_comparison.png
│   ├── network_summary.txt
│   ├── trajectory_prob0.1.png
│   ├── trajectory_prob0.2.png
│   ├── trajectories_comparison.png
│   ├── peak_comparison.png
│   ├── diffusion_summary.txt
│   ├── top_spreaders.png
│   ├── all_spreaders.png
│   ├── centrality_distributions.png
│   ├── influence_correlations.png
│   └── influence_summary.txt
```

---

## Data Dependencies

All visualizations require preprocessed data files in `data/processed/`:

1. **graph_statistics.json**: Network topology metrics
   - num_nodes, num_edges, density, avg_degree
   - metadata: date_range, num_posts

2. **centrality_metrics.json**: Node centrality measures
   - degree_centrality, in_degree_centrality, closeness_centrality
   - For each user node

3. **influential_spreaders.json**: Ranked list of influential users
   - user_id and influence_score
   - Sorted by influence descending

4. **diffusion_trajectory_prob*.json**: SIR trajectories
   - Multiple files for different infection probabilities (0.1, 0.2, 0.3, etc.)
   - Trajectory data: [S, I, R] arrays over time steps

---

## Integration Examples

### Combine Multiple Visualizers

```python
from visualization import NetworkVisualizer, DiffusionVisualizer, InfluenceVisualizer

# Create visualizers
net_viz = NetworkVisualizer()
diff_viz = DiffusionVisualizer()
inf_viz = InfluenceVisualizer()

# Load data
net_viz.load_data()
diff_viz.load_trajectories()
inf_viz.load_data()

# Generate all visualizations
net_viz.visualize_network()
net_viz.visualize_network_interactive_html()

diff_viz.visualize_all_trajectories()
diff_viz.visualize_peak_comparison()

inf_viz.visualize_top_spreaders(top_n=15)
inf_viz.visualize_influence_vs_centrality()

# Generate reports
print(net_viz.generate_summary_report())
print(diff_viz.generate_diffusion_summary())
print(inf_viz.generate_influence_report())
```

### Custom Modification Example

```python
from visualization import NetworkVisualizer
import matplotlib.pyplot as plt

# Custom visualization
viz = NetworkVisualizer()
viz.load_data()

# Access underlying data
graph_stats = viz.graph_stats
centrality = viz.centrality_data
influencers = viz.influential_data

# Create custom analysis
top_10_users = [s['user_id'] for s in influencers['top_spreaders'][:10]]
print(f"Top 10 influencers: {top_10_users}")

# Custom metrics
for user in top_10_users:
    degree = centrality['degree_centrality'].get(user, 0)
    in_degree = centrality['in_degree_centrality'].get(user, 0)
    closeness = centrality['closeness_centrality'].get(user, 0)
    print(f"{user}: degree={degree:.4f}, in-degree={in_degree:.4f}, closeness={closeness:.4f}")
```

---

## Performance Notes

- **Network Graph Construction**: ~0.5 seconds for 15-node networks
- **Interactive HTML Generation**: ~2 seconds with Plotly
- **Dashboard Load Time**: ~3 seconds initial load, <100ms for interactions
- **Memory Usage**: ~150 MB for full data + visualizations

## Troubleshooting

### Missing Output Directory
```python
# Ensure output directory exists
import os
os.makedirs('visualization/output', exist_ok=True)
```

### Import Errors
```python
# If module import fails, add to Python path
import sys
sys.path.insert(0, '/path/to/fake-news-propagation')
```

### Streamlit Port Conflict
```bash
# Run dashboard on different port
streamlit run visualization/dashboard.py --server.port 8502
```

---

## Best Practices

1. **Always Load Data First**: Call `load_data()` or `load_trajectories()` before visualizing
2. **Create Output Directory**: Ensure `visualization/output/` exists
3. **Use Specific Probabilities**: Verify available probability scenarios before visualization
4. **Review Summary Reports**: Text reports provide statistical context for visualizations
5. **Monitor Memory**: For large networks, process visualizations sequentially

---

## Version History

- **v1.0.0**: Initial release with 3 visualizers and interactive dashboard

## Related Documentation

- [ML Models Documentation](../ml_models/MODULE_DOCUMENTATION.md)
- [Propagation Model Documentation](../propagation_model/PROPAGATION_DOCUMENTATION.md)
- [Data Pipeline Documentation](../data_pipeline/PIPELINE_DOCUMENTATION.md)
