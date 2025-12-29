"""
AI Algorithms for Sudoku Solving
Implements Constraint Propagation, AC-3, and Backtracking
"""

import time
import copy
from typing import List, Tuple, Optional, Dict, Set, Generator
from collections import deque
from dataclasses import dataclass
from enum import Enum
from sudoku_board import SudokuBoard


class StepType(Enum):
    """Types of steps in the solving process"""
    ASSIGN = "assign"           # Assigning a value to a cell
    PROPAGATE = "propagate"     # Domain reduction through propagation
    BACKTRACK = "backtrack"     # Backtracking from a dead end
    REVISE = "revise"           # AC-3 arc revision
    TRY = "try"                 # Trying a value (before confirming)
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


class AlgorithmMetrics:
    """Tracks performance metrics for algorithms"""
    
    def __init__(self):
        self.runtime = 0.0
        self.nodes_visited = 0
        self.backtrack_count = 0
        self.domain_reductions = 0
        self.start_time = None
    
    def start(self):
        """Start timing"""
        self.start_time = time.time()
    
    def stop(self):
        """Stop timing and record runtime"""
        if self.start_time:
            self.runtime = time.time() - self.start_time
    
    def reset(self):
        """Reset all metrics"""
        self.runtime = 0.0
        self.nodes_visited = 0
        self.backtrack_count = 0
        self.domain_reductions = 0
        self.start_time = None


class ConstraintPropagationSolver:
    """
    Constraint Propagation Algorithm
    Progressively reduces domains through logical elimination.
    Now includes backtracking to handle hard puzzles.
    """
    
    def __init__(self):
        self.metrics = AlgorithmMetrics()
        self.domains: Dict[Tuple[int, int], Set[int]] = {}
    
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """
        Solve Sudoku using constraint propagation with backtracking
        
        Returns:
            Tuple of (solved_board, metrics)
        """
        self.metrics.reset()
        self.metrics.start()
        
        result = self._solve_recursive(board)
        
        self.metrics.stop()
        
        if result:
            return result, self.metrics
        else:
            return None, self.metrics  # Failed
    
    def _solve_recursive(self, board: SudokuBoard) -> Optional[SudokuBoard]:
        """Recursive solver with constraint propagation"""
        self.metrics.nodes_visited += 1
        
        # 1. Propagate Constraints
        # Initialize domains for this state
        temp_domains = {}
        for row in range(board.size):
            for col in range(board.size):
                if board[row, col] == 0:
                    temp_domains[(row, col)] = board.get_domain(row, col)
                    # Check for immediate conflict (empty domain for empty cell)
                    if not temp_domains[(row, col)]:
                        return None
                else:
                    temp_domains[(row, col)] = {board[row, col]}
        
        # Apply propagation
        changed = True
        while changed:
            changed = False
            
            # Find cells with single value and propagate
            # Use list(items) because we might modify domains (though here we modify board)
            for (row, col), domain in list(temp_domains.items()):
                if len(domain) == 1 and board[row, col] == 0:
                    value = next(iter(domain))
                    if not board.is_valid_move(row, col, value):
                         return None # Conflict detected
                         
                    board[row, col] = value
                    changed = True
                    self.metrics.domain_reductions += 1
                    
                    # Update neighbors locally in temp_domains to reflect this assignment
                    if not self._update_domains(board, temp_domains, row, col, value):
                        return None # Conflict during propagation
        
        # 2. Check if solved
        if board.is_solved():
            return board
        
        # 3. Guess (Backtracking)
        # Select unassigned variable (MRV)
        empty_cells = []
        for r in range(board.size):
            for c in range(board.size):
                if board[r, c] == 0:
                    empty_cells.append((r, c))
        
        if not empty_cells:
            return None # Should have been caught by is_solved or conflict
            
        # Sort by domain size (MRV)
        empty_cells.sort(key=lambda cell: len(temp_domains.get(cell, set())))
        
        row, col = empty_cells[0]
        domain = temp_domains.get((row, col), set())
        
        for value in domain:
            # We don't need is_valid_move here strictly if propagation was correct, 
            # but it is safer to check.
            if board.is_valid_move(row, col, value):
                new_board = board.copy()
                new_board[row, col] = value
                
                result = self._solve_recursive(new_board)
                if result:
                    return result
                
                self.metrics.backtrack_count += 1
                
        return None

    def _update_domains(self, board, domains, row, col, value):
        """Remove value from related domains. Returns False if conflict."""
        # Row
        for c in range(board.size):
            if c != col and (row, c) in domains and board[row, c] == 0:
                if value in domains[(row, c)]:
                    domains[(row, c)].discard(value)
                    self.metrics.domain_reductions += 1
                    if not domains[(row, c)]: return False
        
        # Column
        for r in range(board.size):
            if r != row and (r, col) in domains and board[r, col] == 0:
                if value in domains[(r, col)]:
                    domains[(r, col)].discard(value)
                    self.metrics.domain_reductions += 1
                    if not domains[(r, col)]: return False
        
        # Box
        box_row = (row // board.box_size) * board.box_size
        box_col = (col // board.box_size) * board.box_size
        for r in range(box_row, box_row + board.box_size):
            for c in range(box_col, box_col + board.box_size):
                if (r, c) != (row, col) and (r, c) in domains and board[r, c] == 0:
                    if value in domains[(r, c)]:
                        domains[(r, c)].discard(value)
                        self.metrics.domain_reductions += 1
                        if not domains[(r, c)]: return False
        return True
    
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        """Get a hint for a specific cell"""
        if board[row, col] != 0:
            return None
        
        result, _ = self.solve(board.copy())
        if result and result.is_solved():
            return result[row, col]
        return None
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """
        Solve Sudoku with step-by-step visualization.
        Yields SolveStep objects for each action taken.
        
        Yields:
            SolveStep objects describing each step
        Returns:
            Solved board or None
        """
        self.metrics.reset()
        self.metrics.start()
        
        # Use iterative approach with explicit stack for step visualization
        result = yield from self._solve_with_steps_recursive(board.copy())
        
        self.metrics.stop()
        return result
    
    def _solve_with_steps_recursive(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """Recursive solver with step yielding"""
        self.metrics.nodes_visited += 1
        
        # Initialize domains
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
        
        # Apply propagation with steps
        changed = True
        while changed:
            changed = False
            
            for (row, col), domain in list(temp_domains.items()):
                if len(domain) == 1 and board[row, col] == 0:
                    value = next(iter(domain))
                    if not board.is_valid_move(row, col, value):
                        yield SolveStep(StepType.FAILED, row, col, value,
                                       f"Conflict at ({row+1}, {col+1})")
                        return None
                    
                    board[row, col] = value
                    changed = True
                    self.metrics.domain_reductions += 1
                    
                    yield SolveStep(StepType.PROPAGATE, row, col, value,
                                   f"Propagated {value} to ({row+1}, {col+1})",
                                   copy.deepcopy(temp_domains))
                    
                    # Update neighbors
                    for c in range(board.size):
                        if c != col and (row, c) in temp_domains and board[row, c] == 0:
                            if value in temp_domains[(row, c)]:
                                temp_domains[(row, c)].discard(value)
                                if not temp_domains[(row, c)]:
                                    return None
                    
                    for r in range(board.size):
                        if r != row and (r, col) in temp_domains and board[r, col] == 0:
                            if value in temp_domains[(r, col)]:
                                temp_domains[(r, col)].discard(value)
                                if not temp_domains[(r, col)]:
                                    return None
                    
                    box_row = (row // board.box_size) * board.box_size
                    box_col = (col // board.box_size) * board.box_size
                    for r in range(box_row, box_row + board.box_size):
                        for c in range(box_col, box_col + board.box_size):
                            if (r, c) != (row, col) and (r, c) in temp_domains and board[r, c] == 0:
                                if value in temp_domains[(r, c)]:
                                    temp_domains[(r, c)].discard(value)
                                    if not temp_domains[(r, c)]:
                                        return None
        
        # Check if solved
        if board.is_solved():
            yield SolveStep(StepType.SOLVED, -1, -1, None, "Puzzle solved!")
            return board
        
        # Backtracking with MRV
        empty_cells = [(r, c) for r in range(board.size) for c in range(board.size) if board[r, c] == 0]
        if not empty_cells:
            return None
        
        empty_cells.sort(key=lambda cell: len(temp_domains.get(cell, set())))
        row, col = empty_cells[0]
        domain = temp_domains.get((row, col), set())
        
        for value in domain:
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


class AC3Solver:
    """
    AC-3 (Arc Consistency Algorithm 3)
    Enforces binary consistency between related cells.
    Now includes backtracking to handle hard puzzles (MAC).
    """
    
    def __init__(self):
        self.metrics = AlgorithmMetrics()
        self.domains: Dict[Tuple[int, int], Set[int]] = {}
    
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """
        Solve Sudoku using AC-3 algorithm with backtracking (MAC)
        
        Returns:
            Tuple of (solved_board, metrics)
        """
        self.metrics.reset()
        self.metrics.start()
        
        result = self._solve_recursive(board)
        
        self.metrics.stop()
        
        if result:
            return result, self.metrics
        else:
            return None, self.metrics
            
    def _solve_recursive(self, board: SudokuBoard) -> Optional[SudokuBoard]:
        self.metrics.nodes_visited += 1
        
        # Initialize domains for AC-3
        current_domains = {}
        for row in range(board.size):
            for col in range(board.size):
                if board[row, col] == 0:
                    current_domains[(row, col)] = board.get_domain(row, col)
                    if not current_domains[(row, col)]:
                        return None # Conflict
                else:
                    current_domains[(row, col)] = {board[row, col]}
        
        # Run AC-3
        if not self._ac3(board, current_domains):
            return None # Inconsistent
            
        # Update board with singletons found by AC-3
        # (This is safe because AC-3 ensures consistency)
        for (row, col), domain in current_domains.items():
            if len(domain) == 1 and board[row, col] == 0:
                val = next(iter(domain))
                board[row, col] = val
        
        if board.is_solved():
            return board
            
        # Backtracking
        # Select unassigned variable (MRV)
        empty_cells = [rc for rc, val in current_domains.items() if board[rc[0], rc[1]] == 0]
        if not empty_cells:
            return None
            
        empty_cells.sort(key=lambda rc: len(current_domains[rc]))
        
        row, col = empty_cells[0]
        domain = current_domains[(row, col)]
        
        for value in domain:
            new_board = board.copy()
            new_board[row, col] = value
            
            result = self._solve_recursive(new_board)
            if result:
                return result
            
            self.metrics.backtrack_count += 1
            
        return None

    def _ac3(self, board, domains) -> bool:
        """Run AC-3 algorithm. Returns False if inconsistent."""
        queue = deque()
        
        # Add all binary constraints (arcs)
        # In Sudoku, Arcs are (Cell1, Cell2) where Cell1 and Cell2 are peers (neighbors)
        for row in range(board.size):
            for col in range(board.size):
                # Neighbors
                neighbors = self._get_neighbors(board, row, col)
                for neighbor in neighbors:
                    queue.append(((row, col), neighbor))
        
        while queue:
            (xi, xj) = queue.popleft()
            
            if self._revise(domains, xi, xj):
                if len(domains[xi]) == 0:
                    return False # Empty domain
                
                # Add neighbors of xi (excluding xj) to queue
                neighbors = self._get_neighbors(board, xi[0], xi[1])
                for xk in neighbors:
                    if xk != xj:
                        queue.append((xk, xi))
        return True

    def _get_neighbors(self, board, row, col):
        neighbors = set()
        # Row
        for c in range(board.size):
            if c != col: neighbors.add((row, c))
        # Col
        for r in range(board.size):
            if r != row: neighbors.add((r, col))
        # Box
        box_row = (row // board.box_size) * board.box_size
        box_col = (col // board.box_size) * board.box_size
        for r in range(box_row, box_row + board.box_size):
            for c in range(box_col, box_col + board.box_size):
                if (r, c) != (row, col): neighbors.add((r, c))
        return list(neighbors)

    def _revise(self, domains, xi, xj) -> bool:
        """
        Revise domain of xi based on constraint with xj.
        Constraint: xi != xj
        """
        revised = False
        
        # Check if we need to remove values from domains[xi]
        xj_domain = domains[xj]
        
        # Optimization: If xj has multiple values, xi != xj is always satisfiable (unless domains are equal size 1.. wait)
        # If xj has {v1, v2}, and xi has {v1}, is it consistent? Yes, xj can be v2.
        # Generally for inequality: only if xj is FIXED (size 1), we remove that value from xi.
        if len(xj_domain) == 1:
            val_j = next(iter(xj_domain))
            if val_j in domains[xi]:
                domains[xi].remove(val_j)
                self.metrics.domain_reductions += 1
                revised = True
                
        return revised
    
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        """Get a hint for a specific cell"""
        if board[row, col] != 0:
            return None
        
        result, _ = self.solve(board.copy())
        if result and result.is_solved():
            return result[row, col]
        return None
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """
        Solve Sudoku with step-by-step visualization using AC-3.
        
        Yields:
            SolveStep objects for each action
        Returns:
            Solved board or None
        """
        self.metrics.reset()
        self.metrics.start()
        
        result = yield from self._solve_with_steps_recursive(board.copy())
        
        self.metrics.stop()
        return result
    
    def _solve_with_steps_recursive(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """AC-3 with step visualization"""
        self.metrics.nodes_visited += 1
        
        # Initialize domains
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
        
        # Run AC-3 with steps
        queue = deque()
        for row in range(board.size):
            for col in range(board.size):
                neighbors = self._get_neighbors(board, row, col)
                for neighbor in neighbors:
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
                    
                    neighbors = self._get_neighbors(board, xi[0], xi[1])
                    for xk in neighbors:
                        if xk != xj:
                            queue.append((xk, xi))
        
        # Update board with singletons
        for (row, col), domain in current_domains.items():
            if len(domain) == 1 and board[row, col] == 0:
                val = next(iter(domain))
                board[row, col] = val
                yield SolveStep(StepType.PROPAGATE, row, col, val,
                               f"Assigned {val} to ({row+1}, {col+1})")
        
        if board.is_solved():
            yield SolveStep(StepType.SOLVED, -1, -1, None, "Puzzle solved!")
            return board
        
        # Backtracking
        empty_cells = [rc for rc in current_domains if board[rc[0], rc[1]] == 0]
        if not empty_cells:
            return None
        
        empty_cells.sort(key=lambda rc: len(current_domains[rc]))
        row, col = empty_cells[0]
        domain = current_domains[(row, col)]
        
        for value in domain:
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


class BacktrackingSolver:
    """
    Brute-force Backtracking Search
    Depth-first search with backtracking
    """
    
    def __init__(self, use_mrv: bool = True):
        """
        Initialize backtracking solver
        
        Args:
            use_mrv: Use Minimum Remaining Values heuristic
        """
        self.metrics = AlgorithmMetrics()
        self.use_mrv = use_mrv
    
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """
        Solve Sudoku using backtracking
        
        Returns:
            Tuple of (solved_board, metrics)
        """
        self.metrics.reset()
        self.metrics.start()
        
        result = self._backtrack(board.copy())
        self.metrics.stop()
        
        return result, self.metrics
    
    def _backtrack(self, board: SudokuBoard) -> Optional[SudokuBoard]:
        """Recursive backtracking function"""
        self.metrics.nodes_visited += 1
        
        if board.is_solved():
            return board
        
        # Select next cell
        cell = self._select_unassigned_variable(board)
        if cell is None:
            return None
        
        row, col = cell
        
        # Try values in domain
        domain = board.get_domain(row, col)
        
        # Heuristic: Try to order values? No, standard backtracking just iterates.
        for value in domain:
            if board.is_valid_move(row, col, value):
                board[row, col] = value
                
                result = self._backtrack(board)
                if result is not None:
                    return result
                
                # Backtrack
                board[row, col] = 0
                self.metrics.backtrack_count += 1
        
        return None
    
    def _select_unassigned_variable(self, board: SudokuBoard) -> Optional[Tuple[int, int]]:
        """Select next cell to assign (MRV heuristic if enabled)"""
        empty_cells = board.get_empty_cells()
        
        if not empty_cells:
            return None
        
        if self.use_mrv:
            # Minimum Remaining Values heuristic
            best_cell = None
            min_domain_size = float('inf')
            
            for row, col in empty_cells:
                domain_size = len(board.get_domain(row, col))
                if domain_size < min_domain_size:
                    min_domain_size = domain_size
                    best_cell = (row, col)
            
            return best_cell
        else:
            # Simple: return first empty cell
            return empty_cells[0]
    
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        """Get a hint for a specific cell"""
        if board[row, col] != 0:
            return None
        
        # To get a valid hint, we just need to find ONE solution
        result, _ = self.solve(board)
        if result and result.is_solved():
            return result[row, col]
        return None
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """
        Solve Sudoku with step-by-step visualization using backtracking.
        
        Yields:
            SolveStep objects for each action
        Returns:
            Solved board or None
        """
        self.metrics.reset()
        self.metrics.start()
        
        result = yield from self._backtrack_with_steps(board.copy())
        
        self.metrics.stop()
        return result
    
    def _backtrack_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """Backtracking with step visualization"""
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
                
                # Backtrack
                board[row, col] = 0
                self.metrics.backtrack_count += 1
                
                yield SolveStep(StepType.BACKTRACK, row, col, value,
                               f"Backtracking from ({row+1}, {col+1})")
        
        return None

class IterativeBacktrackingSolver:
    """
    Iterative Backtracking Search using Stack
    Avoids recursion depth limits for large puzzles
    """
    
    def __init__(self):
        self.metrics = AlgorithmMetrics()
    
    def solve(self, board: SudokuBoard) -> Tuple[Optional[SudokuBoard], AlgorithmMetrics]:
        """
        Solve Sudoku using iterative backtracking
        """
        self.metrics.reset()
        self.metrics.start()
        
        # Initial domains calculation
        domains = {}
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
        
        # If no empty cells, it's solved
        if not empty_cells:
            self.metrics.stop()
            return board, self.metrics
            
        # Stack entries: (index_in_empty_cells, current_board, current_domains)
        # Note: We need deep copies of domains if we modify them, 
        # or we accept the cost of re-computing domains or using a reversible structure.
        # For simplicity and correctness with MAC, let's use a simpler approach first:
        # Standard backtracking usually revalidates. 
        # But for 36x36, we need efficiency. 
        # Let's use the explicit stack with state restoration.
        
        # Optimization: Sort empty cells by MRV initially once?
        # A fully dynamic MRV is expensive in iterative without complex state.
        # Let's try static MRV (sort once) for now, which is much better than nothing.
        empty_cells.sort(key=lambda rc: len(domains[rc]))
        
        # Stack: list of (cell_index, available_values)
        # We modify 'board' in place and backtrack by undoing changes.
        stack = []
        cell_idx = 0
        
        while 0 <= cell_idx < len(empty_cells):
            self.metrics.nodes_visited += 1
            row, col = empty_cells[cell_idx]
            
            # If we are visiting this cell for the first time (pushing)
            if cell_idx == len(stack):
                # Get values to try
                # We can re-fetch domain to be safe with current board state
                current_domain = board.get_domain(row, col)
                # Sort values? Randomize?
                values = list(current_domain)
                # Optimization: Least Constraining Value?
                # For now just standard order
                
                stack.append(values)
            
            values = stack[-1]
            
            if not values:
                # Backtrack
                stack.pop()
                board[row, col] = 0 # Undo
                cell_idx -= 1
                self.metrics.backtrack_count += 1
                continue
            
            # Try next value
            value = values.pop()
            
            # Check validity (get_domain already checked it basically, but board changed)
            if board.is_valid_move(row, col, value):
                board[row, col] = value
                cell_idx += 1
            else:
                # Value not valid (caused by other recent assignments?)
                # Actually get_domain checks current board, so if we just calced it, it's valid.
                # BUT if we are returning to this cell from a backtrack, 'values' contains old candidates.
                # Some might have become invalid? No, because we only affect future cells.
                # Wait, simply relying on is_valid_move is safer.
                pass 
                
        self.metrics.stop()
        
        if cell_idx == len(empty_cells):
            return board, self.metrics
        else:
            return None, self.metrics
    
    def get_hint(self, board: SudokuBoard, row: int, col: int) -> Optional[int]:
        """Get a hint for a specific cell"""
        if board[row, col] != 0:
            return None
        
        result, _ = self.solve(board.copy())
        if result and result.is_solved():
            return result[row, col]
        return None
    
    def solve_with_steps(self, board: SudokuBoard) -> Generator[SolveStep, None, Optional[SudokuBoard]]:
        """
        Solve Sudoku with step-by-step visualization using iterative backtracking.
        
        Yields:
            SolveStep objects for each action
        Returns:
            Solved board or None
        """
        self.metrics.reset()
        self.metrics.start()
        
        # Initial domains calculation
        domains = {}
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
                values = list(current_domain)
                stack.append(values)
            
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
