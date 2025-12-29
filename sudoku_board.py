"""
Sudoku Board Class
Handles the Sudoku grid, validation, and basic operations
"""

import copy
from typing import List, Optional, Tuple, Set


class SudokuBoard:
    """Represents a Sudoku board with validation and basic operations"""
    
    def __init__(self, size: int = 9, initial_board: Optional[List[List[int]]] = None):
        """
        Initialize a Sudoku board
        
        Args:
            size: Size of the board (3 for mini-Sudoku, 9 for standard)
            initial_board: Optional initial board state
        """
        self.size = size
        self.box_size = int(size ** 0.5)  # 3 for 9x9, 1 for 3x3
        
        if initial_board:
            self.board = copy.deepcopy(initial_board)
        else:
            self.board = [[0 for _ in range(size)] for _ in range(size)]
    
    def __getitem__(self, pos: Tuple[int, int]) -> int:
        """Get value at position (row, col)"""
        row, col = pos
        return self.board[row][col]
    
    def __setitem__(self, pos: Tuple[int, int], value: int):
        """Set value at position (row, col)"""
        row, col = pos
        if 0 <= value <= self.size:
            self.board[row][col] = value
    
    def get_empty_cells(self) -> List[Tuple[int, int]]:
        """Get list of all empty cell positions"""
        empty = []
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0:
                    empty.append((row, col))
        return empty
    
    def is_valid_move(self, row: int, col: int, value: int) -> bool:
        """
        Check if placing value at (row, col) is valid
        
        Args:
            row: Row index
            col: Column index
            value: Value to place
            
        Returns:
            True if move is valid, False otherwise
        """
        if value == 0:
            return True
        
        # Check row
        for c in range(self.size):
            if c != col and self.board[row][c] == value:
                return False
        
        # Check column
        for r in range(self.size):
            if r != row and self.board[r][col] == value:
                return False
        
        # Check box
        box_row = (row // self.box_size) * self.box_size
        box_col = (col // self.box_size) * self.box_size
        
        for r in range(box_row, box_row + self.box_size):
            for c in range(box_col, box_col + self.box_size):
                if (r, c) != (row, col) and self.board[r][c] == value:
                    return False
        
        return True
    
    def get_conflicts(self, row: int, col: int) -> List[Tuple[int, int]]:
        """
        Get list of cells that conflict with the value at (row, col)
        
        Returns:
            List of conflicting cell positions
        """
        conflicts = []
        value = self.board[row][col]
        
        if value == 0:
            return conflicts
        
        # Check row
        for c in range(self.size):
            if c != col and self.board[row][c] == value:
                conflicts.append((row, c))
        
        # Check column
        for r in range(self.size):
            if r != row and self.board[r][col] == value:
                conflicts.append((r, col))
        
        # Check box
        box_row = (row // self.box_size) * self.box_size
        box_col = (col // self.box_size) * self.box_size
        
        for r in range(box_row, box_row + self.box_size):
            for c in range(box_col, box_col + self.box_size):
                if (r, c) != (row, col) and self.board[r][c] == value:
                    conflicts.append((r, c))
        
        return conflicts
    
    def is_complete(self) -> bool:
        """Check if the board is completely filled"""
        for row in range(self.size):
            for col in range(self.size):
                if self.board[row][col] == 0:
                    return False
        return True
    
    def is_solved(self) -> bool:
        """Check if the board is correctly solved"""
        if not self.is_complete():
            return False
        
        # Check all cells are valid
        for row in range(self.size):
            for col in range(self.size):
                if not self.is_valid_move(row, col, self.board[row][col]):
                    return False
        
        return True
    
    def get_domain(self, row: int, col: int) -> Set[int]:
        """
        Get possible values for a cell
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            Set of possible values
        """
        if self.board[row][col] != 0:
            return {self.board[row][col]}
        
        domain = set(range(1, self.size + 1))
        
        # Remove values from row
        for c in range(self.size):
            if self.board[row][c] in domain:
                domain.remove(self.board[row][c])
        
        # Remove values from column
        for r in range(self.size):
            if self.board[r][col] in domain:
                domain.discard(self.board[r][col])
        
        # Remove values from box
        box_row = (row // self.box_size) * self.box_size
        box_col = (col // self.box_size) * self.box_size
        
        for r in range(box_row, box_row + self.box_size):
            for c in range(box_col, box_col + self.box_size):
                if self.board[r][c] in domain:
                    domain.discard(self.board[r][c])
        
        return domain
    
    def copy(self) -> 'SudokuBoard':
        """Create a deep copy of the board"""
        return SudokuBoard(self.size, self.board)
    
    def __str__(self) -> str:
        """String representation of the board"""
        lines = []
        for row in self.board:
            line = ' '.join(str(val) if val != 0 else '.' for val in row)
            lines.append(line)
        return '\n'.join(lines)
    
    def __eq__(self, other) -> bool:
        """Check if two boards are equal"""
        if not isinstance(other, SudokuBoard):
            return False
        return self.board == other.board

