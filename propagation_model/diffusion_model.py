"""
Epidemic-Inspired Diffusion Model Module

This module implements an SIR (Susceptible-Infected-Recovered) diffusion model
to simulate how misinformation spreads through social networks over time.

Classes:
    SIRDiffusionModel: Simulates information propagation dynamics
"""

import numpy as np
from typing import Dict, List, Tuple, Set
from collections import deque
import json


class SIRDiffusionModel:
    """
    SIR Diffusion Model for misinformation propagation.
    
    States:
        - Susceptible (S): Users who haven't seen the fake news
        - Infected (I): Users actively spreading the fake news
        - Recovered (R): Users who stopped spreading (became skeptical)
    
    Dynamics:
        - S -> I: Susceptible users become infected via neighbors
        - I -> R: Infected users recover (stop spreading)
    """
    
    def __init__(self, graph, infection_prob: float = 0.3, recovery_prob: float = 0.1):
        """
        Initialize the SIR diffusion model.
        
        Args:
            graph: SocialNetworkGraph object
            infection_prob: Probability of infection transmission per timestep (0-1)
            recovery_prob: Probability of recovery per timestep (0-1)
        
        Raises:
            ValueError: If probabilities not in valid range
        """
        if not (0 <= infection_prob <= 1):
            raise ValueError("infection_prob must be between 0 and 1")
        if not (0 <= recovery_prob <= 1):
            raise ValueError("recovery_prob must be between 0 and 1")
        
        self.graph = graph
        self.infection_prob = infection_prob
        self.recovery_prob = recovery_prob
        
        # Simulation state
        self.susceptible = None
        self.infected = None
        self.recovered = None
        self.history = []
        self.is_initialized = False
    
    def initialize_spreading(self, source_nodes: List[str]) -> None:
        """
        Initialize the spreading dynamics with source nodes.
        
        Args:
            source_nodes: List of user IDs to start spreading fake news
        
        Raises:
            ValueError: If source nodes are not in the graph
        """
        graph_nodes = self.graph.nodes
        invalid_nodes = [node for node in source_nodes if node not in graph_nodes]
        if invalid_nodes:
            raise ValueError(f"Source nodes not in graph: {invalid_nodes}")
        
        self.susceptible = graph_nodes - set(source_nodes)
        self.infected = set(source_nodes)
        self.recovered = set()
        self.is_initialized = True
        
        # Record initial state
        self._record_state(timestep=0, source_nodes=source_nodes)
    
    def simulate_step(self, timestep: int) -> Tuple[int, int, int]:
        """
        Simulate one timestep of the SIR model.
        
        Returns:
            Tuple of (susceptible_count, infected_count, recovered_count)
        
        Raises:
            RuntimeError: If spreading not initialized
        """
        if not self.is_initialized:
            raise RuntimeError("Call initialize_spreading() before simulate_step()")
        
        # Process recovery
        recovered_this_step = set()
        for node in self.infected:
            if np.random.rand() < self.recovery_prob:
                recovered_this_step.add(node)
        
        self.infected -= recovered_this_step
        self.recovered |= recovered_this_step
        
        # Process infection
        infected_this_step = set()
        for infected_node in self.infected:
            neighbors = self.graph.get_neighbors(infected_node)
            
            for neighbor in neighbors:
                if neighbor in self.susceptible:
                    # Higher probability for neighbors with stronger connection
                    weight = neighbors[neighbor]
                    adjusted_prob = min(1.0, self.infection_prob * weight)
                    
                    if np.random.rand() < adjusted_prob:
                        infected_this_step.add(neighbor)
        
        # Update states
        self.susceptible -= infected_this_step
        self.infected |= infected_this_step
        
        # Record state
        self._record_state(timestep)
        
        return len(self.susceptible), len(self.infected), len(self.recovered)
    
    def simulate(self, timesteps: int, source_nodes: List[str]) -> Dict:
        """
        Run complete SIR simulation over multiple timesteps.
        
        Args:
            timesteps: Number of timesteps to simulate
            source_nodes: Initial infected users
        
        Returns:
            Dictionary containing:
                - trajectory: List of (S, I, R) counts per timestep
                - peak_infected: Maximum infected count and when it occurred
                - final_spread: Total users who became infected
                - statistics: Detailed propagation statistics
        """
        self.history = []
        self.initialize_spreading(source_nodes)
        
        print(f"Simulating {timesteps} timesteps with {len(source_nodes)} source nodes...")
        print(f"Initial: S={len(self.susceptible)}, I={len(self.infected)}, R={len(self.recovered)}")
        
        for t in range(1, timesteps + 1):
            s, i, r = self.simulate_step(t)
            
            if t % max(1, timesteps // 10) == 0:
                print(f"Timestep {t}: S={s}, I={i}, R={r}")
            
            # Early stopping if no more infected
            if i == 0:
                print(f"Spreading stopped at timestep {t}")
                break
        
        return self.get_simulation_results()
    
    def _record_state(self, timestep: int, source_nodes: List[str] = None) -> None:
        """Record current SIR state to history."""
        state = {
            'timestep': timestep,
            'susceptible': len(self.susceptible),
            'infected': len(self.infected),
            'recovered': len(self.recovered),
            'infected_nodes': list(self.infected),
            'source_nodes': source_nodes
        }
        self.history.append(state)
    
    def get_simulation_results(self) -> Dict:
        """
        Get results from the completed simulation.
        
        Returns:
            Dictionary with trajectory and statistics
        """
        if not self.history:
            raise RuntimeError("No simulation data available")
        
        trajectory = [(s['susceptible'], s['infected'], s['recovered']) 
                      for s in self.history]
        
        infected_counts = [s['infected'] for s in self.history]
        peak_infected = max(infected_counts)
        peak_time = infected_counts.index(peak_infected)
        
        final_state = self.history[-1]
        total_infected = self.graph.get_node_count() - final_state['susceptible']
        
        return {
            'trajectory': trajectory,
            'peak_infected': {
                'count': peak_infected,
                'timestep': peak_time
            },
            'final_spread': {
                'total_infected': total_infected,
                'final_recovered': final_state['recovered'],
                'infection_rate': total_infected / self.graph.get_node_count()
            },
            'statistics': {
                'total_timesteps': len(self.history),
                'total_users': self.graph.get_node_count(),
                'source_nodes': len(self.history[0]['source_nodes']) if self.history[0]['source_nodes'] else 0
            }
        }
    
    def get_trajectory(self) -> List[Tuple[int, int, int]]:
        """Get the complete S-I-R trajectory as list of timestep tuples."""
        return [(s['susceptible'], s['infected'], s['recovered']) 
                for s in self.history]
    
    def get_infected_by_node(self) -> Dict[str, List[int]]:
        """
        Get the timesteps when each user was infected.
        
        Returns:
            Dictionary mapping user_id to timestep of infection
        """
        infection_times = {}
        
        # Start with initial infected
        if self.history and self.history[0]['source_nodes']:
            for node in self.history[0]['source_nodes']:
                infection_times[node] = 0
        
        # Track new infections
        for state in self.history[1:]:
            current_infected = set(state['infected_nodes'])
            previous_infected = set(self.history[self.history.index(state) - 1]['infected_nodes'])
            new_infected = current_infected - previous_infected
            
            for node in new_infected:
                infection_times[node] = state['timestep']
        
        return infection_times
    
    def export_trajectory(self, output_path: str) -> None:
        """
        Export simulation trajectory to JSON file.
        
        Args:
            output_path: Path to save the trajectory file
        """
        results = self.get_simulation_results()
        
        with open(output_path, 'w') as f:
            json.dump({
                'trajectory': results['trajectory'],
                'peak_infected': results['peak_infected'],
                'final_spread': results['final_spread'],
                'statistics': results['statistics']
            }, f, indent=2)
        
        print(f"Trajectory saved to {output_path}")


def main():
    """Example usage of SIRDiffusionModel."""
    from build_graph import SocialNetworkGraph
    
    print("Loading social network graph...")
    graph = SocialNetworkGraph()
    graph.load_from_csv('data/processed/clean_data.csv')
    
    print("Initializing SIR diffusion model...")
    model = SIRDiffusionModel(graph, infection_prob=0.2, recovery_prob=0.05)
    
    # Select source nodes (fake news spreaders)
    source_users = list(graph.nodes)[:3]
    print(f"Source nodes: {source_users}")
    
    # Run simulation
    results = model.simulate(timesteps=20, source_nodes=source_users)
    
    # Display results
    print("\n=== Simulation Results ===")
    print(f"Peak infected: {results['peak_infected']['count']} at timestep {results['peak_infected']['timestep']}")
    print(f"Final infection rate: {results['final_spread']['infection_rate']:.2%}")
    print(f"Total infected: {results['final_spread']['total_infected']} / {results['statistics']['total_users']}")
    
    # Export results
    model.export_trajectory('data/processed/diffusion_results.json')


if __name__ == '__main__':
    main()
