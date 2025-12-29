"""
Sudoku Solver - Source Package
"""

from src.core.board import SudokuBoard
from src.core.generator import PuzzleGenerator
from src.solvers import (
    ConstraintPropagationSolver,
    AC3Solver,
    BacktrackingSolver,
    IterativeBacktrackingSolver
)

__version__ = "2.0.0"
__all__ = [
    'SudokuBoard',
    'PuzzleGenerator',
    'ConstraintPropagationSolver',
    'AC3Solver',
    'BacktrackingSolver',
    'IterativeBacktrackingSolver'
]
