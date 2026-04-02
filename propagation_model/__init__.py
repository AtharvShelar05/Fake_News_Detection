"""
Misinformation Propagation Modeling Module

This module provides tools for modeling how fake news propagates through
social networks using graph-based and epidemic-inspired diffusion models.

Components:
    - build_graph: Constructs social networks from user interaction data
    - diffusion_model: Simulates news propagation using SIR dynamics
    - metrics: Computes centrality and influence metrics
"""

from .build_graph import SocialNetworkGraph
from .diffusion_model import SIRDiffusionModel
from .metrics import PropagationMetrics

__all__ = ['SocialNetworkGraph', 'SIRDiffusionModel', 'PropagationMetrics']
__version__ = '1.0.0'
