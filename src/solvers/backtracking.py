"""
Backtracking Solver for Sudoku
"""

from typing import Optional, Tuple, Generator

from src.core.board import SudokuBoard
from src.core.metrics import AlgorithmMetrics
from src.solvers.base import BaseSolver, StepType, SolveStep


class BacktrackingSolver(BaseSolver):
    """
    Brute-force Backtracking Search
    Depth-first search with backtracking
    """
    
    def __init__(self, use_mrv: bool = True):
        super().__init__()
        self.use_mrv = use_mrv
    
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """Solve using backtracking"""
        self.metrics.reset()
        self.metrics.start()
        result = self._backtrack(board.copy())
        self.metrics.stop()
        return result, self.metrics
    
    def _backtrack(self, board: SudokuBoard) -> Optional[SudokuBoard]:
        """Recursive backtracking"""
        self.metrics.nodes_visited += 1
        
        if board.is_solved():
            return board
        
        cell = self._select_unassigned_variable(board)
        if cell is None:
            return None
        
        row, col = cell
        domain = board.get_domain(row, col)
        
        for value in domain:
            if board.is_valid_move(row, col, value):
                board[row, col] = value
                result = self._backtrack(board)
                if result is not None:
                    return result
                board[row, col] = 0
                self.metrics.backtrack_count += 1
        
        return None
    
    def _select_unassigned_variable(self, board: SudokuBoard) -> Optional[Tuple[int, int]]:
        """Select next cell (MRV heuristic if enabled)"""
        empty_cells = board.get_empty_cells()
        if not empty_cells:
            return None
        
        if self.use_mrv:
            best_cell = None
            min_domain_size = float('inf')
            for row, col in empty_cells:
                domain_size = len(board.get_domain(row, col))
                if domain_size < min_domain_size:
                    min_domain_size = domain_size
                    best_cell = (row, col)
            return best_cell
        else:
            return empty_cells[0]
    
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        if board[row, col] != 0:
            return None
        result, _ = self.solve(board)
        return result[row, col] if result and result.is_solved() else None
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """Solve with step visualization"""
        self.metrics.reset()
        self.metrics.start()
        result = yield from self._backtrack_with_steps(board.copy())
        self.metrics.stop()
        return result
    
    def _backtrack_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        self.metrics.nodes_visited += 1
        
        if board.is_solved():
            yield SolveStep(StepType.SOLVED, -1, -1, None, "Puzzle solved!")
            return board
        
        cell = self._select_unassigned_variable(board)
        if cell is None:
            return None
        
        row, col = cell
        domain = board.get_domain(row, col)
        
        for value in domain:
            if board.is_valid_move(row, col, value):
                yield SolveStep(StepType.TRY, row, col, value,
                               f"Trying {value} at ({row+1}, {col+1})")
                board[row, col] = value
                yield SolveStep(StepType.ASSIGN, row, col, value,
                               f"Assigned {value} to ({row+1}, {col+1})")
                
                result = yield from self._backtrack_with_steps(board)
                if result is not None:
                    return result
                
                board[row, col] = 0
                self.metrics.backtrack_count += 1
                yield SolveStep(StepType.BACKTRACK, row, col, value,
                               f"Backtracking from ({row+1}, {col+1})")
        
        return None
