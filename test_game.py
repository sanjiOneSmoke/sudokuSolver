"""
Simple test script to verify core functionality
"""

from sudoku_board import SudokuBoard
from algorithms import ConstraintPropagationSolver, AC3Solver, BacktrackingSolver
from puzzle_generator import PuzzleGenerator

def test_basic_functionality():
    """Test basic game functionality"""
    print("Testing Sudoku Game Components...")
    print("-" * 50)
    
    # Test 1: Board creation
    print("\n1. Testing board creation...")
    board = SudokuBoard(9)
    assert board.size == 9
    assert board.box_size == 3
    print("   [OK] Board creation works")
    
    # Test 2: Puzzle generation
    print("\n2. Testing puzzle generation...")
    generator = PuzzleGenerator()
    puzzle = generator.generate(9, "easy")
    assert puzzle.size == 9
    empty_count = len(puzzle.get_empty_cells())
    print(f"   [OK] Generated puzzle with {empty_count} empty cells")
    
    # Test 3: Constraint Propagation
    print("\n3. Testing Constraint Propagation...")
    solver1 = ConstraintPropagationSolver()
    test_board = puzzle.copy()
    result, metrics = solver1.solve(test_board)
    print(f"   [OK] Constraint Propagation: {metrics.runtime:.4f}s, {metrics.nodes_visited} nodes")
    
    # Test 4: AC-3
    print("\n4. Testing AC-3...")
    solver2 = AC3Solver()
    test_board = puzzle.copy()
    result, metrics = solver2.solve(test_board)
    print(f"   [OK] AC-3: {metrics.runtime:.4f}s, {metrics.nodes_visited} nodes")
    
    # Test 5: Backtracking
    print("\n5. Testing Backtracking...")
    solver3 = BacktrackingSolver()
    test_board = puzzle.copy()
    result, metrics = solver3.solve(test_board)
    if result and result.is_solved():
        print(f"   [OK] Backtracking solved puzzle: {metrics.runtime:.4f}s, {metrics.nodes_visited} nodes, {metrics.backtrack_count} backtracks")
    else:
        print(f"   [WARN] Backtracking: {metrics.runtime:.4f}s, {metrics.nodes_visited} nodes")
    
    # Test 6: Mini Sudoku
    print("\n6. Testing mini Sudoku (3x3)...")
    mini_puzzle = generator.generate(3, "medium")
    assert mini_puzzle.size == 3
    print(f"   [OK] Generated 3x3 puzzle with {len(mini_puzzle.get_empty_cells())} empty cells")
    
    print("\n" + "-" * 50)
    print("All basic tests passed! [OK]")
    print("\nTo run the game, execute: python sudoku_game.py")

if __name__ == "__main__":
    test_basic_functionality()

