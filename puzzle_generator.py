"""
Sudoku Puzzle Generator
Generates valid Sudoku puzzles of varying difficulty
"""

import random
from typing import List, Tuple
from sudoku_board import SudokuBoard
from algorithms import BacktrackingSolver


class PuzzleGenerator:
    """Generates Sudoku puzzles"""
    
    def __init__(self):
        self.solver = BacktrackingSolver()
    
    def generate(self, size: int = 9, difficulty: str = "medium") -> SudokuBoard:
        """
        Generate a Sudoku puzzle
        
        Args:
            size: Size of the board (3 or 9)
            difficulty: "easy", "medium", or "hard"
            
        Returns:
            A SudokuBoard with some cells filled
        """
        # Create a solved puzzle first
        solved = self._generate_solved(size)
        
        # Remove cells based on difficulty
        puzzle = self._remove_cells(solved, size, difficulty)
        
        return puzzle
    
    def _generate_solved(self, size: int) -> SudokuBoard:
        """Generate a completely solved Sudoku board"""
        board = SudokuBoard(size)
        
        # Fill diagonal boxes first (they don't conflict)
        box_size = int(size ** 0.5)
        for box in range(box_size):
            self._fill_box(board, box * box_size, box * box_size)
        
        # Solve the rest
        solved, _ = self.solver.solve(board)
        return solved if solved else board
    
    def _fill_box(self, board: SudokuBoard, start_row: int, start_col: int):
        """Fill a box with random valid values"""
        values = list(range(1, board.size + 1))
        random.shuffle(values)
        
        idx = 0
        for row in range(start_row, start_row + board.box_size):
            for col in range(start_col, start_col + board.box_size):
                board[row, col] = values[idx]
                idx += 1
    
    def _remove_cells(self, solved: SudokuBoard, size: int, difficulty: str) -> SudokuBoard:
        """Remove cells from solved puzzle based on difficulty"""
        # Create a copy
        puzzle = solved.copy()
        
        # Determine number of cells to keep
        total_cells = size * size
        
        if difficulty == "easy":
            cells_to_keep = int(total_cells * 0.5)  # 50% filled
        elif difficulty == "medium":
            cells_to_keep = int(total_cells * 0.35)  # 35% filled
        else:  # hard
            cells_to_keep = int(total_cells * 0.25)  # 25% filled
        
        # Randomly remove cells
        all_cells = [(r, c) for r in range(size) for c in range(size)]
        random.shuffle(all_cells)
        
        cells_to_remove = total_cells - cells_to_keep
        for i in range(cells_to_remove):
            row, col = all_cells[i]
            puzzle[row, col] = 0
        
        return puzzle
    
    def generate_mini_sudoku(self, difficulty: str = "medium") -> SudokuBoard:
        """Generate a 3x3 mini-Sudoku puzzle"""
        return self.generate(3, difficulty)
    
    def generate_standard_sudoku(self, difficulty: str = "medium") -> SudokuBoard:
        """Generate a 9x9 standard Sudoku puzzle"""
        return self.generate(9, difficulty)

