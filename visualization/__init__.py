"""
Visualization Module: Comprehensive visualization components
for fake news propagation analysis and analysis

Components:
- network_visualization: Social network topology and centrality analysis
- diffusion_visualization: SIR trajectory analysis for different infection probabilities
- influence_visualization: Influence spreader ranking and centrality correlation
- dashboard: Interactive Streamlit dashboard for data exploration

Usage:
    from visualization import NetworkVisualizer, DiffusionVisualizer, InfluenceVisualizer
    
    # Network visualization
    viz_net = NetworkVisualizer()
    viz_net.load_data()
    viz_net.visualize_network()
    
    # Diffusion visualization
    viz_diff = DiffusionVisualizer()
    viz_diff.load_trajectories()
    viz_diff.visualize_all_trajectories()
    
    # Influence visualization
    viz_inf = InfluenceVisualizer()
    viz_inf.load_data()
    viz_inf.visualize_top_spreaders()
    
    # Interactive Dashboard
    # Run: streamlit run visualization/dashboard.py
"""

__version__ = "1.0.0"
__author__ = "Fake News Propagation Project"

try:
    from .network_visualization import NetworkVisualizer
except ImportError:
    from network_visualization import NetworkVisualizer

try:
    from .diffusion_visualization import DiffusionVisualizer
except ImportError:
    from diffusion_visualization import DiffusionVisualizer

try:
    from .influence_visualization import InfluenceVisualizer
except ImportError:
    from influence_visualization import InfluenceVisualizer

__all__ = [
    'NetworkVisualizer',
    'DiffusionVisualizer',
    'InfluenceVisualizer'
]
