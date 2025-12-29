"""
Algorithm Metrics for tracking solver performance
"""

import time
from dataclasses import dataclass, field


@dataclass
class AlgorithmMetrics:
    """Tracks performance metrics for solving algorithms"""
    runtime: float = 0.0
    nodes_visited: int = 0
    backtrack_count: int = 0
    domain_reductions: int = 0
    start_time: float = field(default=None, repr=False)
    
    def reset(self):
        """Reset all metrics"""
        self.runtime = 0.0
        self.nodes_visited = 0
        self.backtrack_count = 0
        self.domain_reductions = 0
        self.start_time = None
    
    def start(self):
        """Start timing"""
        self.start_time = time.time()
    
    def stop(self):
        """Stop timing and calculate runtime"""
        if self.start_time:
            self.runtime = time.time() - self.start_time
    
    def __str__(self):
        return (f"Runtime: {self.runtime:.4f}s, "
                f"Nodes: {self.nodes_visited}, "
                f"Backtracks: {self.backtrack_count}, "
                f"Domain Reductions: {self.domain_reductions}")
