# Visualization Module - Quick Start Guide

## Overview

The Visualization Module provides interactive and static visualizations for analyzing fake news propagation dynamics. Three main components analyze different aspects:

1. **Network Visualization** - Social graph topology and influence metrics
2. **Diffusion Visualization** - SIR epidemic curves for different scenarios  
3. **Influence Visualization** - Spreader rankings and centrality analysis
4. **Interactive Dashboard** - Streamlit web interface for exploration

## Installation

```bash
cd fake-news-propagation
pip install -r visualization/requirements.txt
```

## Running Individual Visualizers

### 1. Network Visualization

```bash
python visualization/network_visualization.py
```

**Generates:**
- `network_visualization.png` - Social network graph with influence sizing
- `network_visualization_interactive.html` - Interactive Plotly visualization
- `centrality_comparison.png` - 3-panel centrality metrics comparison
- `network_summary.txt` - Statistical report

**Analysis:**
- Social network topology with 15 nodes and 78 directed edges
- Node sizes represent user influence scores
- Network density: 0.3714
- Top influencers identified and highlighted

### 2. Diffusion Visualization

```bash
python visualization/diffusion_visualization.py
```

**Generates:**
- `trajectory_prob0.1.png` - SIR curve for 10% infection probability
- `trajectory_prob0.2.png` - SIR curve for 20% infection probability
- `trajectory_prob0.3.png` - SIR curve for 30% infection probability
- `all_trajectories_comparison.png` - Multi-scenario comparison
- `peak_infection_comparison.png` - Peak infection analysis
- `diffusion_summary.txt` - Statistical summary

**Key Findings:**
- Peak infections range from 11-13 depending on probability
- Lower probability (0.1) shows slower but sustained spread
- Higher probability (0.3) shows rapid early peak
- Final spread rates: 32-35% across scenarios

### 3. Influence Visualization

```bash
python visualization/influence_visualization.py
```

**Generates:**
- `top_spreaders.png` - Top 10 most influential users
- `all_spreaders.png` - Scatter plot of all spreader influence
- `centrality_distributions.png` - Distribution of centrality metrics
- `influence_vs_centrality.png` - Correlation between centrality measures
- `influence_report.txt` - Detailed analysis report

**Key Insights:**
- Top 7 users share highest influence (0.6)
- user008, user002, user004, user010 are critical spreaders
- No correlation between degree centrality and influence
- Influence concentrated among core network nodes

## Running the Interactive Dashboard

```bash
streamlit run visualization/dashboard.py
```

Opens browser at `http://localhost:8501` with 5 interactive pages:

1. **Overview** - Project statistics and dataset metadata
2. **Network Analysis** - Interactive network with centrality metrics
3. **Diffusion Dynamics** - Selectable infection probability scenarios
4. **Influence Analysis** - Adjustable top spreader rankings
5. **Comparative Analysis** - Cross-metric distribution analysis

## Output Directory Structure

```
visualization/output/
├── network_visualization.png            # Main network graph
├── network_visualization_interactive.html  # Interactive version
├── centrality_comparison.png            # 3-panel centrality
├── network_summary.txt                  # Network statistics
├── trajectory_prob0.1.png               # Diffusion curve (10%)
├── trajectory_prob0.2.png               # Diffusion curve (20%)
├── trajectory_prob0.3.png               # Diffusion curve (30%)
├── all_trajectories_comparison.png      # Multi-scenario
├── peak_infection_comparison.png        # Peak analysis
├── diffusion_summary.txt                # Diffusion statistics
├── top_spreaders.png                    # Top 10 spreaders
├── all_spreaders.png                    # All spreaders scatter
├── centrality_distributions.png         # Metric distributions
├── influence_vs_centrality.png          # Correlation plots
└── influence_report.txt                 # Influence statistics
```

## Running All Visualizations in Sequence

```python
from visualization import NetworkVisualizer, DiffusionVisualizer, InfluenceVisualizer

# Network analysis
net_viz = NetworkVisualizer()
net_viz.load_data()
net_viz.visualize_network()
net_viz.visualize_network_interactive_html()
print(net_viz.generate_summary_report())

# Diffusion analysis
diff_viz = DiffusionVisualizer()
diff_viz.load_trajectories()
diff_viz.visualize_all_trajectories()
diff_viz.visualize_peak_comparison()
print(diff_viz.generate_diffusion_summary())

# Influence analysis
inf_viz = InfluenceVisualizer()
inf_viz.load_data()
inf_viz.visualize_top_spreaders(top_n=15)
inf_viz.visualize_influence_vs_centrality()
print(inf_viz.generate_influence_report())
```

## Key Metrics

### Network Analysis
- **Nodes**: 15 users
- **Edges**: 78 directed connections
- **Density**: 0.3714 (37% of possible connections)
- **Average Degree**: 5.20
- **Top Spreader**: user008 (influence: 0.6)

### Diffusion Analysis
- **Prob 0.1**: Peak 11, Final recovered 11 (35.5% spread)
- **Prob 0.2**: Peak 13, Final recovered 10 (32.3% spread)
- **Prob 0.3**: Peak 13, Final recovered 11 (35.5% spread)

### Influence Analysis
- **High Influence (0.6)**: 7 users (cluster of core spreaders)
- **Medium Influence (0.3-0.55)**: 5 users
- **Low Influence (<0.3)**: 3 users
- **Mean Influence**: 0.403

## Interpreting Results

### Network Graphs
- **Node Size**: Proportional to user influence (larger = more influential)
- **Node Color**: Represents degree centrality (darker = more connections)
- **Edge Direction**: Shows information flow direction
- **Network Density**: 0.37 indicates sparse but connected network

### Diffusion Curves
- **S(t)**: Susceptible decreases over time
- **I(t)**: Infected peaks then decreases
- **R(t)**: Recovered increases monotonically
- **Higher Probability**: Faster spread, higher early peaks

### Influence Distributions
- **Skewed Distribution**: Few highly influential users dominate
- **Centrality Correlation**: Different centrality types show different patterns
- **Network Roles**: Users cluster into influencers vs. regular nodes

## Customization

### Python API
```python
from visualization import NetworkVisualizer

viz = NetworkVisualizer()
viz.load_data()

# Custom visualization
fig = viz.visualize_network()  # Returns matplotlib figure

# Access raw data
print(viz.graph_stats)
print(viz.centrality_data)
print(viz.influential_data)
```

### Dashboard Customization
Edit `visualization/dashboard.py` to:
- Change color schemes (replace viridis with other colormaps)
- Adjust slider ranges for top_n spreaders
- Add custom analysis sections
- Integrate additional data sources

## Troubleshooting

**Issue: "Cannot find data files"**
```python
import os
print(os.getcwd())  # Check working directory
# Run from: fake-news-propagation/
```

**Issue: "Port already in use" (Dashboard)**
```bash
streamlit run visualization/dashboard.py --server.port 8502
```

**Issue: Missing matplotlib displays**
```python
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
```

## Files Structure

```
visualization/
├── __init__.py                          # Module initialization
├── network_visualization.py             # Network graph visualizer
├── diffusion_visualization.py           # SIR trajectory visualizer
├── influence_visualization.py           # Influence metrics visualizer
├── dashboard.py                         # Streamlit interactive app
├── requirements.txt                     # Dependencies
├── VISUALIZATION_DOCUMENTATION.md       # Full docs
├── QUICKSTART.md                        # This file
└── output/                              # Generated visualizations
    └── [15 output files from visualizations]
```

## Performance

- Network graph: ~0.5 seconds
- Interactive HTML: ~2 seconds
- Dashboard startup: ~3 seconds
- Memory usage: ~150 MB

## Dependencies

- **matplotlib** - Static visualizations
- **networkx** - Graph processing
- **plotly** - Interactive visualizations
- **streamlit** - Web dashboard
- **numpy** - Numerical operations
- **pandas** - Data manipulation

## Next Steps

1. ✅ **View Static Visualizations**: Open PNG files in image viewer
2. ✅ **Explore Interactive HTML**: Open in web browser
3. ✅ **Launch Dashboard**: Run streamlit command
4. ✅ **Integrate with ML Models**: Use predictions with propagation data
5. ✅ **Custom Analysis**: Modify visualizer classes for your needs

## Related Modules

- [ML Models](../ml_models/README.md) - Fake news detection models
- [Propagation Model](../propagation_model/README.md) - SIR simulation engine
- [Data Pipeline](../data_pipeline/PIPELINE_DOCUMENTATION.md) - Data processing

---

**Version**: 1.0.0  
**Last Updated**: 2024  
**Status**: Production Ready ✓
