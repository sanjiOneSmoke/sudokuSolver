#!/usr/bin/env python3
"""
Sudoku Solver - Main Entry Point
Run this file to start the game: python main.py
"""

import sys
import os

# Add src to path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk
from tkinter import ttk, messagebox
import time
from typing import Optional, Dict, Tuple

from src.core.board import SudokuBoard
from src.core.generator import PuzzleGenerator
from src.core.metrics import AlgorithmMetrics
from src.solvers import (
    ConstraintPropagationSolver, 
    AC3Solver, 
    BacktrackingSolver, 
    IterativeBacktrackingSolver,
    StepType,
    SolveStep
)
from src.ui.animation import AnimationController, AnimationState


class SudokuGame:
    """Main Sudoku Game Application with GUI"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🧩 Intelligent Sudoku Solver and Analyzer")
        self.root.minsize(1000, 950)
        self._center_window(1100, 1000)
        self.root.configure(bg="#f5f7fa")
        
        # Color scheme
        self.colors = {
            'bg': '#f5f7fa',
            'primary': '#4a90e2',
            'secondary': '#50c878',
            'accent': '#ff6b6b',
            'text': '#2c3e50',
            'cell_bg': '#ffffff',
            'cell_selected': '#fff9c4',
            'cell_original': '#e8e8e8',
            'cell_error': '#ffcccc',
            'cell_hint': '#c8e6c9',
            'cell_try': '#fff3e0',
            'cell_assign': '#c8e6c9',
            'cell_backtrack': '#ffcdd2',
            'cell_propagate': '#bbdefb',
            'cell_revise': '#e1bee7',
            'border': '#d0d0d0',
            'border_strong': '#4a90e2'
        }
        
        # Game state
        self.current_board: Optional[SudokuBoard] = None
        self.original_board: Optional[SudokuBoard] = None
        self.board_size = 9
        self.difficulty = "medium"
        self.selected_algorithm = "Constraint Propagation"
        self.hints_used = 0
        self.start_time = None
        self.timer_running = False
        self.move_history = []
        self.redo_stack = []
        
        # Animation controller
        self.animation = AnimationController()
        self.animation.on_step = self._on_animation_step
        self.animation.on_state_change = self._on_animation_state_change
        self.animation.on_finished = self._on_animation_finished
        self.animation_timer_id = None
        self.animation_board_state: Dict[Tuple[int, int], int] = {}  # Track board state during animation
        
        # Solvers
        self.solvers = {
            "Constraint Propagation": ConstraintPropagationSolver(),
            "AC-3": AC3Solver(),
            "Backtracking": BacktrackingSolver(),
            "Iterative Backtracking": IterativeBacktrackingSolver()
        }
        
        # Generator
        self.generator = PuzzleGenerator()
        
        # UI elements
        self.cells: Dict[Tuple[int, int], tk.Entry] = {}
        self.conflict_cells: set = set()
        self.selected_cell: Optional[Tuple[int, int]] = None
        
        self._create_ui()
    
    def _center_window(self, width: int, height: int):
        """Center window on screen"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")
    
    def _create_ui(self):
        """Create the user interface"""
        # Main container
        main_frame = tk.Frame(self.root, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title = tk.Label(main_frame, text="🧩 Intelligent Sudoku Solver",
                        font=("Arial", 24, "bold"),
                        bg=self.colors['bg'], fg=self.colors['text'])
        title.pack(pady=(0, 20))
        
        # Control panel
        control_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Board size
        tk.Label(control_frame, text="Board Size:",
                font=("Arial", 10), bg=self.colors['bg']).pack(side=tk.LEFT, padx=5)
        self.size_var = tk.StringVar(value="9x9")
        size_menu = ttk.Combobox(control_frame, textvariable=self.size_var,
                                values=["3x3", "9x9", "16x16", "25x25"], state="readonly", width=8)
        size_menu.pack(side=tk.LEFT, padx=5)
        
        # Difficulty
        tk.Label(control_frame, text="Difficulty:",
                font=("Arial", 10), bg=self.colors['bg']).pack(side=tk.LEFT, padx=(20, 5))
        self.diff_var = tk.StringVar(value="Medium")
        diff_menu = ttk.Combobox(control_frame, textvariable=self.diff_var,
                                values=["Easy", "Medium", "Hard"], state="readonly", width=10)
        diff_menu.pack(side=tk.LEFT, padx=5)
        
        # Algorithm
        tk.Label(control_frame, text="Algorithm:",
                font=("Arial", 10), bg=self.colors['bg']).pack(side=tk.LEFT, padx=(20, 5))
        self.algo_var = tk.StringVar(value="Constraint Propagation")
        algo_menu = ttk.Combobox(control_frame, textvariable=self.algo_var,
                                values=list(self.solvers.keys()), state="readonly", width=20)
        algo_menu.pack(side=tk.LEFT, padx=5)
        
        # Button panel
        button_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        button_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Style for buttons
        style = ttk.Style()
        style.configure('Primary.TButton', font=('Arial', 9, 'bold'), padding=(12, 8))
        style.configure('Secondary.TButton', font=('Arial', 9), padding=(10, 6))
        style.configure('Animation.TButton', font=('Arial', 9, 'bold'), padding=(12, 8))
        
        # Button row 1
        row1 = ttk.Frame(button_frame)
        row1.pack(fill=tk.X, pady=2)
        
        ttk.Button(row1, text="🆕 New Puzzle", command=self._new_puzzle,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(row1, text="💡 Get Hint", command=self._get_hint,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(row1, text="⚡ Solve", command=self._solve_puzzle,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(row1, text="📊 Compare", command=self._compare_algorithms,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(row1, text="🎬 Animate", command=self._solve_animated,
                  style='Animation.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        
        # Button row 2
        row2 = ttk.Frame(button_frame)
        row2.pack(fill=tk.X, pady=2)
        
        ttk.Button(row2, text="↶ Undo", command=self._undo_move,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(row2, text="↷ Redo", command=self._redo_move,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(row2, text="🗑️ Clear", command=self._clear_board,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(row2, text="✓ Check", command=self._check_solution,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(row2, text="📈 Stats", command=self._show_stats,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        
        # Animation controls (hidden by default)
        self.animation_frame = tk.Frame(button_frame, bg="#fff3e0")
        self._create_animation_controls()
        
        # Board container
        self.board_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        self.board_frame.pack(pady=20)
        
        # Status bar
        status_frame = tk.Frame(main_frame, bg=self.colors['bg'])
        status_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.status_label = tk.Label(status_frame, text="Click 'New Puzzle' to start!",
                                     font=("Arial", 11), bg=self.colors['bg'], fg=self.colors['text'])
        self.status_label.pack(side=tk.LEFT)
        
        self.timer_label = tk.Label(status_frame, text="Time: 00:00",
                                    font=("Arial", 11), bg=self.colors['bg'], fg=self.colors['text'])
        self.timer_label.pack(side=tk.RIGHT)
        
        # Metrics display
        self.metrics_label = tk.Label(main_frame, text="",
                                      font=("Consolas", 10), bg=self.colors['bg'], fg=self.colors['text'])
        self.metrics_label.pack(pady=(10, 0))
    
    def _create_animation_controls(self):
        """Create animation control panel"""
        tk.Label(self.animation_frame, text="Animation:", font=("Arial", 9, "bold"),
                bg="#fff3e0").pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(self.animation_frame, text="⏸️ Pause",
                                   command=self._toggle_animation, width=8)
        self.pause_btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(self.animation_frame, text="⏹️ Stop",
                 command=self._stop_animation, width=6).pack(side=tk.LEFT, padx=2)
        
        tk.Button(self.animation_frame, text="⏭️ Step",
                 command=self._step_animation, width=6).pack(side=tk.LEFT, padx=2)
        
        tk.Label(self.animation_frame, text="Speed:", bg="#fff3e0").pack(side=tk.LEFT, padx=(10, 2))
        self.speed_scale = tk.Scale(self.animation_frame, from_=10, to=500,
                                    orient=tk.HORIZONTAL, length=100, bg="#fff3e0",
                                    command=self._on_speed_change)
        self.speed_scale.set(100)
        self.speed_scale.pack(side=tk.LEFT, padx=2)
        
        self.animation_status = tk.Label(self.animation_frame, text="",
                                        font=("Arial", 9), bg="#fff3e0", fg="#333")
        self.animation_status.pack(side=tk.LEFT, padx=10)
    
    def _new_puzzle(self):
        """Generate a new puzzle"""
        size_str = self.size_var.get()
        self.board_size = int(size_str.split('x')[0])
        self.difficulty = self.diff_var.get().lower()
        
        self.current_board = self.generator.generate(self.board_size, self.difficulty)
        self.original_board = self.current_board.copy()
        
        self.hints_used = 0
        self.move_history = []
        self.redo_stack = []
        self.start_time = time.time()
        self.timer_running = True
        
        self._create_board_ui()
        self._update_timer()
        self.status_label.config(text=f"New {self.board_size}x{self.board_size} {self.difficulty} puzzle generated!")
    
    def _create_board_ui(self):
        """Create board grid UI"""
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        
        self.cells.clear()
        
        if not self.current_board:
            return
        
        cell_size = max(40, 400 // self.board_size)
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Frame for border effects
                box_row, box_col = row // self.current_board.box_size, col // self.current_board.box_size
                
                padx = (3 if col % self.current_board.box_size == 0 and col > 0 else 1, 1)
                pady = (3 if row % self.current_board.box_size == 0 and row > 0 else 1, 1)
                
                cell_frame = tk.Frame(self.board_frame, bg=self.colors['border_strong'] if (box_row + box_col) % 2 == 0 else self.colors['border'])
                cell_frame.grid(row=row, column=col, padx=padx, pady=pady)
                
                # Entry widget
                entry = tk.Entry(cell_frame, width=2, font=("Arial", int(cell_size * 0.4), "bold"),
                               justify="center", bd=0, highlightthickness=2,
                               highlightbackground=self.colors['border'],
                               highlightcolor=self.colors['primary'])
                entry.pack(padx=1, pady=1)
                entry.config(width=2)
                entry.configure(font=("Arial", int(cell_size * 0.4), "bold"))
                
                value = self.current_board[row, col]
                if value != 0:
                    entry.insert(0, str(value))
                    entry.config(state="readonly", bg=self.colors['cell_original'],
                               disabledforeground=self.colors['text'])
                else:
                    entry.config(bg=self.colors['cell_bg'])
                    entry.bind('<KeyRelease>', lambda e, r=row, c=col: self._on_cell_change(r, c, e))
                    entry.bind('<FocusIn>', lambda e, r=row, c=col: self._on_cell_focus(r, c))
                
                self.cells[(row, col)] = entry
    
    def _on_cell_change(self, row: int, col: int, event):
        """Handle cell value change"""
        if not self.current_board or self.original_board[row, col] != 0:
            return
        
        entry = self.cells[(row, col)]
        value = entry.get()
        
        if value == '':
            old_value = self.current_board[row, col]
            self.current_board[row, col] = 0
            self.move_history.append((row, col, old_value, 0))
            self.redo_stack.clear()
            entry.config(bg=self.colors['cell_bg'])
        elif value.isdigit() and 1 <= int(value) <= self.board_size:
            new_value = int(value)
            old_value = self.current_board[row, col]
            
            if self.current_board.is_valid_move(row, col, new_value):
                self.current_board[row, col] = new_value
                self.move_history.append((row, col, old_value, new_value))
                self.redo_stack.clear()
                entry.config(bg=self.colors['cell_bg'])
            else:
                entry.config(bg=self.colors['cell_error'])
                self.current_board[row, col] = new_value
        else:
            entry.delete(0, tk.END)
    
    def _on_cell_focus(self, row: int, col: int):
        """Handle cell focus"""
        self.selected_cell = (row, col)
    
    def _get_hint(self):
        """Get hint for selected cell"""
        if not self.selected_cell or not self.current_board:
            messagebox.showinfo("Hint", "Please select an empty cell first!")
            return
        
        row, col = self.selected_cell
        if self.current_board[row, col] != 0:
            messagebox.showinfo("Hint", "Cell already has a value!")
            return
        
        solver = self.solvers[self.algo_var.get()]
        hint = solver.get_hint(self.current_board.copy(), row, col)
        
        if hint:
            entry = self.cells[(row, col)]
            entry.delete(0, tk.END)
            entry.insert(0, str(hint))
            entry.config(bg=self.colors['cell_hint'])
            self.current_board[row, col] = hint
            self.hints_used += 1
            self.status_label.config(text=f"Hint: {hint} at ({row+1}, {col+1})")
        else:
            messagebox.showerror("Hint", "Could not find a valid hint!")
    
    def _solve_puzzle(self):
        """Solve the puzzle"""
        if not self.current_board:
            messagebox.showinfo("Solve", "Please generate a puzzle first!")
            return
        
        solver = self.solvers[self.algo_var.get()]
        result, metrics = solver.solve(self.current_board.copy())
        
        if result and result.is_solved():
            self.current_board = result
            self._create_board_ui()
            self.timer_running = False
            self.status_label.config(text="Puzzle solved!")
            self.metrics_label.config(text=str(metrics))
        else:
            messagebox.showerror("Solve", "Could not solve the puzzle!")
    
    def _compare_algorithms(self):
        """Compare all algorithms with tabular display"""
        if not self.current_board:
            messagebox.showinfo("Compare", "Please generate a puzzle first!")
            return
        
        # Calculate timeout based on board size
        timeout_map = {9: 10, 16: 30, 25: 120}  # 9x9: 10s, 16x16: 30s, 25x25: 2min
        timeout_seconds = timeout_map.get(self.board_size, 10)
        
        # Show loading message
        self.status_label.config(text=f"Comparing algorithms... (max {timeout_seconds}s per algorithm)")
        self.root.update()
        
        import threading
        import queue
        
        def solve_with_timeout(solver, board, result_queue, name):
            try:
                result, metrics = solver.solve(board)
                solved = result and result.is_solved()
                result_queue.put({
                    'name': name,
                    'solved': solved,
                    'runtime': metrics.runtime,
                    'nodes': metrics.nodes_visited,
                    'backtracks': metrics.backtrack_count,
                    'reductions': metrics.domain_reductions,
                    'timeout': False
                })
            except Exception as e:
                result_queue.put({
                    'name': name,
                    'solved': False,
                    'runtime': 0,
                    'nodes': 0,
                    'backtracks': 0,
                    'reductions': 0,
                    'timeout': True,
                    'error': str(e)
                })
        
        # Collect results with timeout
        results = []
        
        for name, solver in self.solvers.items():
            result_queue = queue.Queue()
            thread = threading.Thread(target=solve_with_timeout, 
                                     args=(solver, self.current_board.copy(), result_queue, name))
            thread.daemon = True
            thread.start()
            thread.join(timeout=timeout_seconds)
            
            if thread.is_alive():
                # Timeout occurred
                results.append({
                    'name': name,
                    'solved': False,
                    'runtime': timeout_seconds,
                    'nodes': 0,
                    'backtracks': 0,
                    'reductions': 0,
                    'timeout': True
                })
            else:
                try:
                    result = result_queue.get_nowait()
                    results.append(result)
                except queue.Empty:
                    results.append({
                        'name': name,
                        'solved': False,
                        'runtime': 0,
                        'nodes': 0,
                        'backtracks': 0,
                        'reductions': 0,
                        'timeout': True
                    })
        
        # Create comparison window
        comp_window = tk.Toplevel(self.root)
        comp_window.title("📊 Algorithm Comparison")
        comp_window.geometry("700x350")
        comp_window.configure(bg="#f5f7fa")
        comp_window.transient(self.root)
        comp_window.grab_set()
        
        # Title
        tk.Label(comp_window, text="📊 Algorithm Performance Comparison",
                font=("Arial", 16, "bold"), bg="#f5f7fa", fg="#2c3e50").pack(pady=(15, 10))
        
        tk.Label(comp_window, text=f"Board: {self.board_size}x{self.board_size} | Difficulty: {self.difficulty}",
                font=("Arial", 10), bg="#f5f7fa", fg="#666").pack(pady=(0, 15))
        
        # Table frame
        table_frame = tk.Frame(comp_window, bg="#f5f7fa")
        table_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)
        
        # Headers
        headers = ["Algorithm", "Status", "Runtime", "Nodes", "Backtracks", "Reductions"]
        col_widths = [22, 10, 12, 10, 12, 12]
        
        for col, (header, width) in enumerate(zip(headers, col_widths)):
            cell = tk.Label(table_frame, text=header, font=("Arial", 10, "bold"),
                          bg="#4a90e2", fg="white", width=width, pady=8, padx=5)
            cell.grid(row=0, column=col, sticky="nsew", padx=1, pady=1)
        
        # Find best values for highlighting
        solved_results = [r for r in results if r['solved']]
        if solved_results:
            best_runtime = min(r['runtime'] for r in solved_results)
            best_nodes = min(r['nodes'] for r in solved_results)
        else:
            best_runtime = best_nodes = None
        
        # Data rows
        for row_idx, data in enumerate(results, start=1):
            bg_color = "#ffffff" if row_idx % 2 == 1 else "#f0f0f0"
            
            # Algorithm name
            tk.Label(table_frame, text=data['name'], font=("Arial", 10),
                    bg=bg_color, fg="#2c3e50", width=col_widths[0], pady=6, anchor="w", padx=5).grid(
                    row=row_idx, column=0, sticky="nsew", padx=1, pady=1)
            
            # Status
            if data.get('timeout'):
                status_text = "⏱️ Timeout"
                status_color = "#f39c12"
            elif data['solved']:
                status_text = "✅ Solved"
                status_color = "#27ae60"
            else:
                status_text = "❌ Failed"
                status_color = "#e74c3c"
            tk.Label(table_frame, text=status_text, font=("Arial", 10, "bold"),
                    bg=bg_color, fg=status_color, width=col_widths[1], pady=6).grid(
                    row=row_idx, column=1, sticky="nsew", padx=1, pady=1)
            
            # Runtime (highlight best)
            runtime_bg = "#c8e6c9" if data['solved'] and data['runtime'] == best_runtime else bg_color
            tk.Label(table_frame, text=f"{data['runtime']:.4f}s", font=("Arial", 10),
                    bg=runtime_bg, fg="#2c3e50", width=col_widths[2], pady=6).grid(
                    row=row_idx, column=2, sticky="nsew", padx=1, pady=1)
            
            # Nodes (highlight best)
            nodes_bg = "#c8e6c9" if data['solved'] and data['nodes'] == best_nodes else bg_color
            tk.Label(table_frame, text=str(data['nodes']), font=("Arial", 10),
                    bg=nodes_bg, fg="#2c3e50", width=col_widths[3], pady=6).grid(
                    row=row_idx, column=3, sticky="nsew", padx=1, pady=1)
            
            # Backtracks
            tk.Label(table_frame, text=str(data['backtracks']), font=("Arial", 10),
                    bg=bg_color, fg="#2c3e50", width=col_widths[4], pady=6).grid(
                    row=row_idx, column=4, sticky="nsew", padx=1, pady=1)
            
            # Domain reductions
            tk.Label(table_frame, text=str(data['reductions']), font=("Arial", 10),
                    bg=bg_color, fg="#2c3e50", width=col_widths[5], pady=6).grid(
                    row=row_idx, column=5, sticky="nsew", padx=1, pady=1)
        
        # Legend
        legend_frame = tk.Frame(comp_window, bg="#f5f7fa")
        legend_frame.pack(pady=(10, 5))
        tk.Label(legend_frame, text="🟢 = Best performance", font=("Arial", 9),
                bg="#f5f7fa", fg="#666").pack(side=tk.LEFT, padx=10)
        
        # Close button
        tk.Button(comp_window, text="Close", command=comp_window.destroy,
                 font=("Arial", 10), width=15, bg="#4a90e2", fg="white",
                 activebackground="#357abd", cursor="hand2").pack(pady=15)
    
    def _solve_animated(self):
        """Solve with animation"""
        if not self.current_board:
            messagebox.showinfo("Animate", "Please generate a puzzle first!")
            return
        
        # Reset board to original state for animation
        self.current_board = self.original_board.copy()
        self._create_board_ui()
        
        # Initialize animation board state tracking
        self.animation_board_state = {}
        for row in range(self.board_size):
            for col in range(self.board_size):
                self.animation_board_state[(row, col)] = self.current_board[row, col]
        
        solver = self.solvers[self.algo_var.get()]
        step_gen = solver.solve_with_steps(self.current_board.copy())
        
        self.animation.reset()
        self.animation.start(step_gen)
        self.animation.set_speed_ms(self.speed_scale.get())
        
        self.animation_frame.pack(fill=tk.X, pady=5)
        self._run_animation_step()
    
    def _run_animation_step(self):
        """Execute one animation step"""
        if not self.animation.is_playing():
            return
        
        step = self.animation.step_forward()
        if step and self.animation.should_continue():
            delay = self.animation.get_delay_ms()
            self.animation_timer_id = self.root.after(delay, self._run_animation_step)
    
    def _on_animation_step(self, step: SolveStep, index: int):
        """Handle animation step"""
        self.animation_status.config(text=f"Step {index + 1}: {step.message}")
        
        color_map = {
            StepType.ASSIGN: self.colors['cell_assign'],
            StepType.TRY: self.colors['cell_try'],
            StepType.BACKTRACK: self.colors['cell_backtrack'],
            StepType.PROPAGATE: self.colors['cell_propagate'],
            StepType.REVISE: self.colors['cell_revise']
        }
        color = color_map.get(step.step_type, self.colors['cell_bg'])
        
        if 0 <= step.row < self.board_size and 0 <= step.col < self.board_size:
            entry = self.cells.get((step.row, step.col))
            if entry:
                # Only modify non-original cells
                if self.original_board and self.original_board[step.row, step.col] == 0:
                    entry.config(bg=color, state='normal')
                    
                    if step.step_type == StepType.BACKTRACK:
                        # Clear the cell on backtrack and update state
                        entry.delete(0, tk.END)
                        self.animation_board_state[(step.row, step.col)] = 0
                        # Keep backtrack color visible longer
                        self.root.after(300, lambda r=step.row, c=step.col: self._reset_cell_color(r, c))
                    
                    elif step.step_type == StepType.TRY:
                        # Show TRY value with distinctive color - don't reset immediately
                        if step.value is not None:
                            entry.delete(0, tk.END)
                            entry.insert(0, str(step.value))
                        # TRY color stays until ASSIGN or BACKTRACK
                    
                    elif step.step_type == StepType.ASSIGN:
                        # Assign value and update state
                        if step.value is not None:
                            entry.delete(0, tk.END)
                            entry.insert(0, str(step.value))
                            self.animation_board_state[(step.row, step.col)] = step.value
                        # Reset to normal color after delay
                        self.root.after(150, lambda r=step.row, c=step.col: self._reset_cell_color(r, c))
                    
                    elif step.step_type == StepType.PROPAGATE:
                        # Propagate shows constraint deduction
                        if step.value is not None:
                            entry.delete(0, tk.END)
                            entry.insert(0, str(step.value))
                            self.animation_board_state[(step.row, step.col)] = step.value
                        self.root.after(150, lambda r=step.row, c=step.col: self._reset_cell_color(r, c))
                    
                    elif step.step_type == StepType.REVISE:
                        # REVISE shows domain reduction - flash the cell briefly
                        # Don't change value, just show that domain was reduced
                        self.root.after(100, lambda r=step.row, c=step.col: self._reset_cell_color(r, c))
    
    def _reset_cell_color(self, row: int, col: int):
        """Reset cell color"""
        if (row, col) in self.cells:
            entry = self.cells[(row, col)]
            if self.original_board and self.original_board[row, col] != 0:
                entry.config(bg=self.colors['cell_original'])
            else:
                entry.config(bg=self.colors['cell_bg'])
    
    def _on_animation_state_change(self, state: AnimationState):
        """Handle animation state change"""
        if state == AnimationState.PAUSED:
            self.pause_btn.config(text="▶️ Resume")
        elif state == AnimationState.PLAYING:
            self.pause_btn.config(text="⏸️ Pause")
    
    def _on_animation_finished(self, success: bool):
        """Handle animation finished"""
        self.animation_frame.pack_forget()
        if success:
            self.status_label.config(text="Animation complete - Puzzle solved!")
        else:
            self.status_label.config(text="Animation complete - No solution found")
    
    def _toggle_animation(self):
        """Toggle pause/resume"""
        if self.animation.is_paused():
            self.animation.resume()
            self._run_animation_step()
        else:
            self.animation.pause()
    
    def _stop_animation(self):
        """Stop animation"""
        self.animation.stop()
        if self.animation_timer_id:
            self.root.after_cancel(self.animation_timer_id)
        self.animation_frame.pack_forget()
    
    def _step_animation(self):
        """Single step"""
        if self.animation.is_paused() or self.animation.state == AnimationState.IDLE:
            if self.animation.state == AnimationState.IDLE:
                self._solve_animated()
                self.animation.pause()
        self.animation.step_forward()
    
    def _on_speed_change(self, value):
        """Handle speed change"""
        self.animation.set_speed_ms(int(value))
    
    def _undo_move(self):
        """Undo last move"""
        if not self.move_history:
            return
        
        row, col, old_value, new_value = self.move_history.pop()
        self.redo_stack.append((row, col, old_value, new_value))
        
        self.current_board[row, col] = old_value
        entry = self.cells[(row, col)]
        entry.delete(0, tk.END)
        if old_value != 0:
            entry.insert(0, str(old_value))
    
    def _redo_move(self):
        """Redo last undone move"""
        if not self.redo_stack:
            return
        
        row, col, old_value, new_value = self.redo_stack.pop()
        self.move_history.append((row, col, old_value, new_value))
        
        self.current_board[row, col] = new_value
        entry = self.cells[(row, col)]
        entry.delete(0, tk.END)
        if new_value != 0:
            entry.insert(0, str(new_value))
    
    def _clear_board(self):
        """Clear to original state"""
        if not self.original_board:
            return
        
        self.current_board = self.original_board.copy()
        self.move_history.clear()
        self.redo_stack.clear()
        self._create_board_ui()
    
    def _check_solution(self):
        """Check current solution"""
        if not self.current_board:
            return
        
        if self.current_board.is_solved():
            elapsed = time.time() - self.start_time if self.start_time else 0
            self.timer_running = False
            messagebox.showinfo("Congratulations! 🎉",
                              f"Puzzle solved correctly!\n\n"
                              f"Time: {int(elapsed // 60)}:{int(elapsed % 60):02d}\n"
                              f"Hints used: {self.hints_used}")
        else:
            conflicts = []
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if self.current_board[row, col] != 0:
                        c = self.current_board.get_conflicts(row, col)
                        if c:
                            conflicts.append((row, col))
            
            if conflicts:
                messagebox.showwarning("Not Correct", f"Found {len(conflicts)} conflicting cells!")
            else:
                messagebox.showinfo("Incomplete", "Puzzle is not complete yet!")
    
    def _show_stats(self):
        """Show game statistics"""
        if not self.current_board:
            messagebox.showinfo("Stats", "No puzzle loaded!")
            return
        
        empty = len([1 for r in range(self.board_size) for c in range(self.board_size)
                    if self.current_board[r, c] == 0])
        filled = self.board_size ** 2 - empty
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        stats = f"Board: {self.board_size}x{self.board_size}\n"
        stats += f"Difficulty: {self.difficulty}\n"
        stats += f"Cells filled: {filled}/{self.board_size ** 2}\n"
        stats += f"Hints used: {self.hints_used}\n"
        stats += f"Time elapsed: {int(elapsed // 60)}:{int(elapsed % 60):02d}"
        
        messagebox.showinfo("Statistics", stats)
    
    def _update_timer(self):
        """Update timer display"""
        if self.timer_running and self.start_time:
            elapsed = time.time() - self.start_time
            mins = int(elapsed // 60)
            secs = int(elapsed % 60)
            self.timer_label.config(text=f"Time: {mins:02d}:{secs:02d}")
            self.root.after(1000, self._update_timer)


def main():
    """Main entry point"""
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()
