"""
Base classes and types for Sudoku Solvers
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, Tuple, Dict, Set, Generator

from src.core.board import SudokuBoard
from src.core.metrics import AlgorithmMetrics


class StepType(Enum):
    """Types of steps during solving for visualization"""
    ASSIGN = "assign"           # Assigning a value to a cell
    PROPAGATE = "propagate"     # Propagating constraints
    BACKTRACK = "backtrack"     # Backtracking from a failed path
    REVISE = "revise"           # AC-3 revision
    TRY = "try"                 # Trying a value
    SOLVED = "solved"           # Puzzle solved
    FAILED = "failed"           # No solution found


@dataclass
class SolveStep:
    """Represents a single step in the solving process"""
    step_type: StepType
    row: int
    col: int
    value: Optional[int]
    message: str
    domains: Optional[Dict[Tuple[int, int], Set[int]]] = None


class BaseSolver(ABC):
    """Abstract base class for all Sudoku solvers"""
    
    def __init__(self):
        self.metrics = AlgorithmMetrics()
    
    @abstractmethod
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """
        Solve the Sudoku puzzle.
        
        Args:
            board: The puzzle to solve
            
        Returns:
            Tuple of (solved_board or None, metrics)
        """
        pass
    
    @abstractmethod
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        """
        Get a hint for a specific cell.
        
        Args:
            board: Current board state
            row: Row index
            col: Column index
            
        Returns:
            The correct value for the cell, or None
        """
        pass
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """
        Solve with step-by-step visualization.
        Default implementation just calls solve().
        Override for detailed step visualization.
        
        Yields:
            SolveStep objects for each action
        Returns:
            Solved board or None
        """
        result, _ = self.solve(board)
        if result:
            yield SolveStep(StepType.SOLVED, -1, -1, None, "Puzzle solved!")
        else:
            yield SolveStep(StepType.FAILED, -1, -1, None, "No solution found")
        return result
