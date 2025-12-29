"""
Iterative Backtracking Solver for Sudoku
Uses explicit stack to avoid recursion depth limits
"""

from typing import Optional, Tuple, Dict, Set, Generator

from src.core.board import SudokuBoard
from src.core.metrics import AlgorithmMetrics
from src.solvers.base import BaseSolver, StepType, SolveStep


class IterativeBacktrackingSolver(BaseSolver):
    """
    Iterative Backtracking Search using Stack
    Avoids recursion depth limits for large puzzles
    """
    
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """Solve using iterative backtracking"""
        self.metrics.reset()
        self.metrics.start()
        
        # Initial domains
        domains: Dict[Tuple[int, int], Set[int]] = {}
        empty_cells = []
        for row in range(board.size):
            for col in range(board.size):
                if board[row, col] == 0:
                    dom = board.get_domain(row, col)
                    if not dom:
                        self.metrics.stop()
                        return None, self.metrics
                    domains[(row, col)] = dom
                    empty_cells.append((row, col))
        
        if not empty_cells:
            self.metrics.stop()
            return board, self.metrics
        
        # Sort by MRV
        empty_cells.sort(key=lambda rc: len(domains[rc]))
        
        # Stack-based backtracking
        stack = []
        cell_idx = 0
        
        while 0 <= cell_idx < len(empty_cells):
            self.metrics.nodes_visited += 1
            row, col = empty_cells[cell_idx]
            
            if cell_idx == len(stack):
                current_domain = board.get_domain(row, col)
                stack.append(list(current_domain))
            
            values = stack[-1]
            
            if not values:
                stack.pop()
                board[row, col] = 0
                cell_idx -= 1
                self.metrics.backtrack_count += 1
                continue
            
            value = values.pop()
            if board.is_valid_move(row, col, value):
                board[row, col] = value
                cell_idx += 1
        
        self.metrics.stop()
        
        if cell_idx == len(empty_cells):
            return board, self.metrics
        else:
            return None, self.metrics
    
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        if board[row, col] != 0:
            return None
        result, _ = self.solve(board.copy())
        return result[row, col] if result and result.is_solved() else None
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """Solve with step visualization"""
        self.metrics.reset()
        self.metrics.start()
        
        domains: Dict[Tuple[int, int], Set[int]] = {}
        empty_cells = []
        for row in range(board.size):
            for col in range(board.size):
                if board[row, col] == 0:
                    dom = board.get_domain(row, col)
                    if not dom:
                        self.metrics.stop()
                        yield SolveStep(StepType.FAILED, row, col, None,
                                       f"Empty domain at ({row+1}, {col+1})")
                        return None
                    domains[(row, col)] = dom
                    empty_cells.append((row, col))
        
        if not empty_cells:
            self.metrics.stop()
            yield SolveStep(StepType.SOLVED, -1, -1, None, "Puzzle solved!")
            return board
        
        empty_cells.sort(key=lambda rc: len(domains[rc]))
        
        stack = []
        cell_idx = 0
        
        while 0 <= cell_idx < len(empty_cells):
            self.metrics.nodes_visited += 1
            row, col = empty_cells[cell_idx]
            
            if cell_idx == len(stack):
                current_domain = board.get_domain(row, col)
                stack.append(list(current_domain))
            
            values = stack[-1]
            
            if not values:
                stack.pop()
                board[row, col] = 0
                cell_idx -= 1
                self.metrics.backtrack_count += 1
                if cell_idx >= 0:
                    prev_row, prev_col = empty_cells[cell_idx]
                    yield SolveStep(StepType.BACKTRACK, prev_row, prev_col, None,
                                   f"Backtracking from ({prev_row+1}, {prev_col+1})")
                continue
            
            value = values.pop()
            yield SolveStep(StepType.TRY, row, col, value,
                           f"Trying {value} at ({row+1}, {col+1})")
            
            if board.is_valid_move(row, col, value):
                board[row, col] = value
                cell_idx += 1
                yield SolveStep(StepType.ASSIGN, row, col, value,
                               f"Assigned {value} to ({row+1}, {col+1})")
        
        self.metrics.stop()
        
        if cell_idx == len(empty_cells):
            yield SolveStep(StepType.SOLVED, -1, -1, None, "Puzzle solved!")
            return board
        else:
            yield SolveStep(StepType.FAILED, -1, -1, None, "No solution found")
            return None
