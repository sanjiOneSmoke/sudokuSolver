"""
Constraint Propagation Solver for Sudoku
"""

import copy
from typing import Optional, Tuple, Dict, Set, Generator

from src.core.board import SudokuBoard
from src.core.metrics import AlgorithmMetrics
from src.solvers.base import BaseSolver, StepType, SolveStep


class ConstraintPropagationSolver(BaseSolver):
    """
    Constraint Propagation Algorithm
    Progressively reduces domains through logical elimination.
    Includes backtracking for hard puzzles.
    """
    
    def __init__(self):
        super().__init__()
        self.domains: Dict[Tuple[int, int], Set[int]] = {}
    
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """Solve using constraint propagation with backtracking"""
        self.metrics.reset()
        self.metrics.start()
        
        result = self._solve_recursive(board)
        
        self.metrics.stop()
        return (result, self.metrics) if result else (None, self.metrics)
    
    def _solve_recursive(self, board: SudokuBoard) -> Optional[SudokuBoard]:
        """Recursive solver with constraint propagation"""
        self.metrics.nodes_visited += 1
        
        # Initialize domains
        temp_domains = {}
        for row in range(board.size):
            for col in range(board.size):
                if board[row, col] == 0:
                    temp_domains[(row, col)] = board.get_domain(row, col)
                    if not temp_domains[(row, col)]:
                        return None
                else:
                    temp_domains[(row, col)] = {board[row, col]}
        
        # Propagate constraints
        changed = True
        while changed:
            changed = False
            for (row, col), domain in list(temp_domains.items()):
                if len(domain) == 1 and board[row, col] == 0:
                    value = next(iter(domain))
                    if not board.is_valid_move(row, col, value):
                        return None
                    board[row, col] = value
                    changed = True
                    self.metrics.domain_reductions += 1
                    if not self._update_domains(board, temp_domains, row, col, value):
                        return None
        
        if board.is_solved():
            return board
        
        # Backtracking with MRV
        empty_cells = [(r, c) for r in range(board.size) for c in range(board.size) 
                       if board[r, c] == 0]
        if not empty_cells:
            return None
        
        empty_cells.sort(key=lambda cell: len(temp_domains.get(cell, set())))
        row, col = empty_cells[0]
        
        for value in temp_domains.get((row, col), set()):
            if board.is_valid_move(row, col, value):
                new_board = board.copy()
                new_board[row, col] = value
                result = self._solve_recursive(new_board)
                if result:
                    return result
                self.metrics.backtrack_count += 1
        
        return None
    
    def _update_domains(self, board, domains, row, col, value):
        """Remove value from related domains"""
        # Row
        for c in range(board.size):
            if c != col and (row, c) in domains and board[row, c] == 0:
                domains[(row, c)].discard(value)
                if not domains[(row, c)]:
                    return False
        
        # Column
        for r in range(board.size):
            if r != row and (r, col) in domains and board[r, col] == 0:
                domains[(r, col)].discard(value)
                if not domains[(r, col)]:
                    return False
        
        # Box
        box_row = (row // board.box_size) * board.box_size
        box_col = (col // board.box_size) * board.box_size
        for r in range(box_row, box_row + board.box_size):
            for c in range(box_col, box_col + board.box_size):
                if (r, c) != (row, col) and (r, c) in domains and board[r, c] == 0:
                    domains[(r, c)].discard(value)
                    if not domains[(r, c)]:
                        return False
        return True
    
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        """Get hint for a cell"""
        if board[row, col] != 0:
            return None
        result, _ = self.solve(board.copy())
        return result[row, col] if result and result.is_solved() else None
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """Solve with step-by-step visualization"""
        self.metrics.reset()
        self.metrics.start()
        result = yield from self._solve_with_steps_recursive(board.copy())
        self.metrics.stop()
        return result
    
    def _solve_with_steps_recursive(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """Recursive solver with step visualization"""
        self.metrics.nodes_visited += 1
        
        temp_domains = {}
        for row in range(board.size):
            for col in range(board.size):
                if board[row, col] == 0:
                    temp_domains[(row, col)] = board.get_domain(row, col)
                    if not temp_domains[(row, col)]:
                        yield SolveStep(StepType.FAILED, row, col, None,
                                       f"Empty domain at ({row+1}, {col+1})")
                        return None
                else:
                    temp_domains[(row, col)] = {board[row, col]}
        
        changed = True
        while changed:
            changed = False
            for (row, col), domain in list(temp_domains.items()):
                if len(domain) == 1 and board[row, col] == 0:
                    value = next(iter(domain))
                    if not board.is_valid_move(row, col, value):
                        return None
                    board[row, col] = value
                    changed = True
                    self.metrics.domain_reductions += 1
                    yield SolveStep(StepType.PROPAGATE, row, col, value,
                                   f"Propagated {value} to ({row+1}, {col+1})",
                                   copy.deepcopy(temp_domains))
                    if not self._update_domains(board, temp_domains, row, col, value):
                        return None
        
        if board.is_solved():
            yield SolveStep(StepType.SOLVED, -1, -1, None, "Puzzle solved!")
            return board
        
        empty_cells = [(r, c) for r in range(board.size) for c in range(board.size) 
                       if board[r, c] == 0]
        if not empty_cells:
            return None
        
        empty_cells.sort(key=lambda cell: len(temp_domains.get(cell, set())))
        row, col = empty_cells[0]
        
        for value in temp_domains.get((row, col), set()):
            if board.is_valid_move(row, col, value):
                yield SolveStep(StepType.TRY, row, col, value,
                               f"Trying {value} at ({row+1}, {col+1})")
                
                new_board = board.copy()
                new_board[row, col] = value
                
                yield SolveStep(StepType.ASSIGN, row, col, value,
                               f"Assigned {value} to ({row+1}, {col+1})")
                
                result = yield from self._solve_with_steps_recursive(new_board)
                if result:
                    return result
                
                self.metrics.backtrack_count += 1
                yield SolveStep(StepType.BACKTRACK, row, col, value,
                               f"Backtracking from ({row+1}, {col+1})")
        
        return None
