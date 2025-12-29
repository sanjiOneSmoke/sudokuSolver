"""
AC-3 (Arc Consistency Algorithm 3) Solver for Sudoku
"""

import copy
from collections import deque
from typing import Optional, Tuple, Dict, Set, List, Generator

from src.core.board import SudokuBoard
from src.core.metrics import AlgorithmMetrics
from src.solvers.base import BaseSolver, StepType, SolveStep


class AC3Solver(BaseSolver):
    """
    AC-3 (Arc Consistency Algorithm 3)
    Enforces binary consistency between related cells.
    Includes backtracking (MAC) for hard puzzles.
    """
    
    def __init__(self):
        super().__init__()
        self.domains: Dict[Tuple[int, int], Set[int]] = {}
    
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """Solve using AC-3 with backtracking (MAC)"""
        self.metrics.reset()
        self.metrics.start()
        result = self._solve_recursive(board)
        self.metrics.stop()
        return (result, self.metrics) if result else (None, self.metrics)
    
    def _solve_recursive(self, board: SudokuBoard) -> Optional[SudokuBoard]:
        self.metrics.nodes_visited += 1
        
        # Initialize domains
        current_domains = {}
        for row in range(board.size):
            for col in range(board.size):
                if board[row, col] == 0:
                    current_domains[(row, col)] = board.get_domain(row, col)
                    if not current_domains[(row, col)]:
                        return None
                else:
                    current_domains[(row, col)] = {board[row, col]}
        
        # Run AC-3
        if not self._ac3(board, current_domains):
            return None
        
        # Update board with singletons
        for (row, col), domain in current_domains.items():
            if len(domain) == 1 and board[row, col] == 0:
                board[row, col] = next(iter(domain))
        
        if board.is_solved():
            return board
        
        # Backtracking with MRV
        empty_cells = [rc for rc, val in current_domains.items() if board[rc[0], rc[1]] == 0]
        if not empty_cells:
            return None
        
        empty_cells.sort(key=lambda rc: len(current_domains[rc]))
        row, col = empty_cells[0]
        
        for value in current_domains[(row, col)]:
            new_board = board.copy()
            new_board[row, col] = value
            result = self._solve_recursive(new_board)
            if result:
                return result
            self.metrics.backtrack_count += 1
        
        return None
    
    def _ac3(self, board, domains) -> bool:
        """Run AC-3 algorithm"""
        queue = deque()
        
        for row in range(board.size):
            for col in range(board.size):
                for neighbor in self._get_neighbors(board, row, col):
                    queue.append(((row, col), neighbor))
        
        while queue:
            (xi, xj) = queue.popleft()
            if self._revise(domains, xi, xj):
                if len(domains[xi]) == 0:
                    return False
                for xk in self._get_neighbors(board, xi[0], xi[1]):
                    if xk != xj:
                        queue.append((xk, xi))
        return True
    
    def _get_neighbors(self, board, row, col) -> List[Tuple[int, int]]:
        """Get all neighbors (same row, column, or box)"""
        neighbors = set()
        for c in range(board.size):
            if c != col:
                neighbors.add((row, c))
        for r in range(board.size):
            if r != row:
                neighbors.add((r, col))
        box_row = (row // board.box_size) * board.box_size
        box_col = (col // board.box_size) * board.box_size
        for r in range(box_row, box_row + board.box_size):
            for c in range(box_col, box_col + board.box_size):
                if (r, c) != (row, col):
                    neighbors.add((r, c))
        return list(neighbors)
    
    def _revise(self, domains, xi, xj) -> bool:
        """Revise domain of xi based on xj"""
        revised = False
        xj_domain = domains[xj]
        if len(xj_domain) == 1:
            val_j = next(iter(xj_domain))
            if val_j in domains[xi]:
                domains[xi].remove(val_j)
                self.metrics.domain_reductions += 1
                revised = True
        return revised
    
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        if board[row, col] != 0:
            return None
        result, _ = self.solve(board.copy())
        return result[row, col] if result and result.is_solved() else None
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """Solve with step visualization"""
        self.metrics.reset()
        self.metrics.start()
        result = yield from self._solve_with_steps_recursive(board.copy())
        self.metrics.stop()
        return result
    
    def _solve_with_steps_recursive(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        self.metrics.nodes_visited += 1
        
        current_domains = {}
        for row in range(board.size):
            for col in range(board.size):
                if board[row, col] == 0:
                    current_domains[(row, col)] = board.get_domain(row, col)
                    if not current_domains[(row, col)]:
                        yield SolveStep(StepType.FAILED, row, col, None,
                                       f"Empty domain at ({row+1}, {col+1})")
                        return None
                else:
                    current_domains[(row, col)] = {board[row, col]}
        
        # AC-3 with steps
        queue = deque()
        for row in range(board.size):
            for col in range(board.size):
                for neighbor in self._get_neighbors(board, row, col):
                    queue.append(((row, col), neighbor))
        
        while queue:
            (xi, xj) = queue.popleft()
            xj_domain = current_domains[xj]
            if len(xj_domain) == 1:
                val_j = next(iter(xj_domain))
                if val_j in current_domains[xi]:
                    current_domains[xi].discard(val_j)
                    self.metrics.domain_reductions += 1
                    yield SolveStep(StepType.REVISE, xi[0], xi[1], val_j,
                                   f"Revised ({xi[0]+1}, {xi[1]+1}): removed {val_j}",
                                   copy.deepcopy(current_domains))
                    if len(current_domains[xi]) == 0:
                        yield SolveStep(StepType.FAILED, xi[0], xi[1], None,
                                       f"Empty domain at ({xi[0]+1}, {xi[1]+1})")
                        return None
                    for xk in self._get_neighbors(board, xi[0], xi[1]):
                        if xk != xj:
                            queue.append((xk, xi))
        
        for (row, col), domain in current_domains.items():
            if len(domain) == 1 and board[row, col] == 0:
                val = next(iter(domain))
                board[row, col] = val
                yield SolveStep(StepType.PROPAGATE, row, col, val,
                               f"Assigned {val} to ({row+1}, {col+1})")
        
        if board.is_solved():
            yield SolveStep(StepType.SOLVED, -1, -1, None, "Puzzle solved!")
            return board
        
        empty_cells = [rc for rc in current_domains if board[rc[0], rc[1]] == 0]
        if not empty_cells:
            yield SolveStep(StepType.FAILED, -1, -1, None, "No empty cells but puzzle not solved")
            return None
        
        empty_cells.sort(key=lambda rc: len(current_domains[rc]))
        row, col = empty_cells[0]
        
        for value in current_domains[(row, col)]:
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
        
        yield SolveStep(StepType.FAILED, row, col, None, f"All values exhausted at ({row+1}, {col+1})")
        return None
