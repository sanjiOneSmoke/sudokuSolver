"""
Main Sudoku Game Application
GUI implementation using tkinter
"""

import tkinter as tk
from tkinter import ttk, messagebox
import time
from typing import Optional, Dict, List, Tuple
from sudoku_board import SudokuBoard
from algorithms import (
    ConstraintPropagationSolver,
    AC3Solver,
    BacktrackingSolver,
    IterativeBacktrackingSolver,
    AlgorithmMetrics,
    StepType,
    SolveStep
)
from puzzle_generator import PuzzleGenerator
from animation_controller import AnimationController, AnimationState, AnimationSpeed


class SudokuGame:
    """Main game class with GUI"""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("🧩 Intelligent Sudoku Solver and Analyzer")
        
        # Set minimum window size
        self.root.minsize(1000, 950)
        
        # Center window on screen
        self._center_window(1100, 1000)
        
        self.root.configure(bg="#f5f7fa")
        
        # Color scheme - static palette
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
        self.start_time = None
        self.hints_used = 0
        
        # History for undo/redo
        self.history: List[SudokuBoard] = []
        self.history_index = -1
        self.max_history = 50
        
        # Statistics
        self.stats = {
            'puzzles_solved': 0,
            'total_time': 0.0,
            'total_hints': 0,
            'best_time': float('inf')
        }
        
        # Timer
        self.timer_running = False
        self.timer_id = None
        
        # Animation controller
        self.animation = AnimationController()
        self.animation.on_step = self._on_animation_step
        self.animation.on_state_change = self._on_animation_state_change
        self.animation.on_finished = self._on_animation_finished
        self.animation_board: Optional[SudokuBoard] = None
        self.animation_timer_id = None
        
        # Solvers - now includes Iterative Backtracking
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
        self.selected_cell: Optional[Tuple[int, int]] = None  # Track selected cell
        
        self._create_ui()
    
    def _create_ui(self):
        """Create the user interface"""
        # Title frame - modern gradient-like design
        title_frame = tk.Frame(self.root, bg=self.colors['primary'], height=75)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        # Title with shadow effect
        title_container = tk.Frame(title_frame, bg=self.colors['primary'])
        title_container.pack(expand=True, fill=tk.BOTH)
        
        title_label = tk.Label(title_container, 
                              text="🧩 Intelligent Sudoku Solver", 
                              font=("Arial", 22, "bold"),
                              bg=self.colors['primary'],
                              fg="white")
        title_label.pack(pady=20)
        
        # Subtitle
        subtitle_label = tk.Label(title_container,
                                text="AI-Powered Puzzle Solver & Analyzer",
                                font=("Arial", 10),
                                bg=self.colors['primary'],
                                fg="#e3f2fd")
        subtitle_label.pack(pady=(0, 15))
        
        # Top frame for controls - modern design
        control_frame = tk.Frame(self.root, bg="#ffffff", relief=tk.FLAT)
        control_frame.pack(fill=tk.X, padx=15, pady=15)
        
        # Configure modern styles
        style = ttk.Style()
        style.theme_use('clam')  # Modern theme
        
        # Custom combobox style
        style.configure('Modern.TCombobox',
                       fieldbackground='white',
                       background='white',
                       borderwidth=2,
                       relief=tk.FLAT,
                       padding=8,
                       font=('Arial', 10))
        style.map('Modern.TCombobox',
                 fieldbackground=[('readonly', '#f8f9fa')],
                 background=[('readonly', '#f8f9fa')],
                 bordercolor=[('focus', self.colors['primary'])],
                 lightcolor=[('focus', self.colors['primary'])],
                 darkcolor=[('focus', self.colors['primary'])])
        
        # Modern label style
        label_style = {
            'font': ('Arial', 11, 'bold'),
            'bg': '#ffffff',
            'fg': '#2c3e50',
            'padx': 8
        }
        
        # Control items container with modern card design
        controls_card = tk.Frame(control_frame, bg="#f8f9fa", relief=tk.FLAT, borderwidth=1)
        controls_card.pack(fill=tk.X, padx=0, pady=0)
        
        controls_inner = tk.Frame(controls_card, bg="#f8f9fa")
        controls_inner.pack(fill=tk.X, padx=20, pady=15)
        
        # Size selection with icon
        size_container = tk.Frame(controls_inner, bg="#f8f9fa")
        size_container.pack(side=tk.LEFT, padx=15, pady=5)
        
        size_label = tk.Label(size_container, text="📐 Board Size:", **label_style)
        size_label.pack(side=tk.LEFT, padx=(0, 8))
        
        size_var = tk.StringVar(value="9x9")
        size_combo = ttk.Combobox(size_container, textvariable=size_var, 
                                   values=["3x3", "9x9", "16x16", "25x25", "36x36"], width=10, 
                                   state="readonly", style='Modern.TCombobox')
        size_combo.pack(side=tk.LEFT)
        size_combo.bind("<<ComboboxSelected>>", 
                       lambda e: self._on_size_change(size_var.get()))
        
        # Difficulty selection with icon
        diff_container = tk.Frame(controls_inner, bg="#f8f9fa")
        diff_container.pack(side=tk.LEFT, padx=15, pady=5)
        
        diff_label = tk.Label(diff_container, text="⚡ Difficulty:", **label_style)
        diff_label.pack(side=tk.LEFT, padx=(0, 8))
        
        self.diff_var = tk.StringVar(value="medium")
        diff_combo = ttk.Combobox(diff_container, textvariable=self.diff_var,
                                   values=["easy", "medium", "hard"], width=10, 
                                   state="readonly", style='Modern.TCombobox')
        diff_combo.pack(side=tk.LEFT)
        diff_combo.bind("<<ComboboxSelected>>", self._on_difficulty_change)
        
        # Algorithm selection with icon
        algo_container = tk.Frame(controls_inner, bg="#f8f9fa")
        algo_container.pack(side=tk.LEFT, padx=15, pady=5)
        
        algo_label = tk.Label(algo_container, text="🤖 Algorithm:", **label_style)
        algo_label.pack(side=tk.LEFT, padx=(0, 8))
        
        algo_var = tk.StringVar(value="Constraint Propagation")
        algo_combo = ttk.Combobox(algo_container, textvariable=algo_var,
                                  values=list(self.solvers.keys()), width=22, 
                                  state="readonly", style='Modern.TCombobox')
        algo_combo.pack(side=tk.LEFT)
        algo_combo.bind("<<ComboboxSelected>>",
                       lambda e: setattr(self, 'selected_algorithm', algo_var.get()))
        
        # Buttons with better styling - wrapped for responsiveness
        button_frame = tk.Frame(control_frame, bg="#ffffff")
        button_frame.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        # Button style configuration - modern flat design
        style.configure('Primary.TButton', 
                       font=('Arial', 10, 'bold'),
                       padding=(15, 10),
                       relief=tk.FLAT,
                       borderwidth=0)
        style.map('Primary.TButton',
                 background=[('active', '#357abd'), ('!active', self.colors['primary'])],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        style.configure('Secondary.TButton',
                       font=('Arial', 9),
                       padding=(12, 8),
                       relief=tk.FLAT,
                       borderwidth=0)
        style.map('Secondary.TButton',
                 background=[('active', '#45b869'), ('!active', self.colors['secondary'])],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        # Animation button style
        style.configure('Animation.TButton',
                       font=('Arial', 9, 'bold'),
                       padding=(12, 8),
                       relief=tk.FLAT,
                       borderwidth=0)
        style.map('Animation.TButton',
                 background=[('active', '#e65100'), ('!active', '#ff9800')],
                 foreground=[('active', 'white'), ('!active', 'white')])
        
        # Create two rows for buttons
        button_row1 = ttk.Frame(button_frame)
        button_row1.pack(fill=tk.X, pady=2)
        
        button_row2 = ttk.Frame(button_frame)
        button_row2.pack(fill=tk.X, pady=2)
        
        # Primary buttons - Row 1 (5 buttons)
        ttk.Button(button_row1, text="🆕 New Puzzle", 
                  command=self._new_puzzle,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(button_row1, text="💡 Get Hint", 
                  command=self._get_hint,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(button_row1, text="⚡ Solve", 
                  command=self._solve_puzzle,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(button_row1, text="📊 Compare", 
                  command=self._compare_algorithms,
                  style='Primary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(button_row1, text="🎬 Animate", 
                  command=self._solve_animated,
                  style='Animation.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        
        # Secondary buttons - Row 2 (5 buttons)
        ttk.Button(button_row2, text="↶ Undo", 
                  command=self._undo_move,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(button_row2, text="↷ Redo", 
                  command=self._redo_move,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(button_row2, text="🗑️ Clear", 
                  command=self._clear_board,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(button_row2, text="✓ Check", 
                  command=self._check_solution,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        ttk.Button(button_row2, text="📈 Stats", 
                  command=self._show_stats,
                  style='Secondary.TButton').pack(side=tk.LEFT, padx=4, expand=True, fill=tk.X)
        
        # Animation control frame (hidden by default)
        self.animation_frame = tk.Frame(button_frame, bg="#fff3e0")
        # Will be shown when animation starts
        
        self._create_animation_controls()
        
        # Board frame with better styling - centered (don't take all space)
        board_container = tk.Frame(self.root, bg=self.colors['bg'])
        board_container.pack(expand=True, fill=tk.BOTH, padx=25, pady=15)
        
        # Center the board - limit expansion to leave room for bottom sections
        board_wrapper = tk.Frame(board_container, bg=self.colors['bg'])
        board_wrapper.pack(expand=True)
        
        self.board_frame = tk.Frame(board_wrapper, 
                                    bg=self.colors['bg'],
                                    relief=tk.RAISED,
                                    borderwidth=2)
        self.board_frame.pack(expand=False)  # Don't expand, keep centered
        
        # Ensure board container doesn't push bottom sections out of view
        # This is handled by pack order (bottom sections packed last)
        
        # Metrics frame with better styling (pack first, will be above status)
        self.metrics_frame = tk.LabelFrame(self.root, 
                                          text="📈 Algorithm Metrics", 
                                          font=("Arial", 10, "bold"),
                                          bg=self.colors['bg'],
                                          fg=self.colors['text'],
                                          relief=tk.RAISED,
                                          borderwidth=2)
        self.metrics_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 5))
        
        # Status frame with timer - better styling (pack last, will be at very bottom)
        self.status_frame = tk.Frame(self.root, bg="#e8e8e8", relief=tk.RAISED, borderwidth=1)
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=15, pady=(0, 10))
        
        status_left = tk.Frame(self.status_frame, bg="#e8e8e8")
        status_left.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=15, pady=10)
        
        self.status_label = tk.Label(status_left, 
                                    text="Ready to play! 🎮",
                                    font=("Arial", 11),
                                    bg="#e8e8e8",
                                    fg=self.colors['text'])
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        # Timer with icon
        timer_frame = tk.Frame(status_left, bg="#e8e8e8")
        timer_frame.pack(side=tk.LEFT, padx=15)
        
        timer_icon = tk.Label(timer_frame, text="⏱️", font=("Arial", 12), bg="#e8e8e8")
        timer_icon.pack(side=tk.LEFT, padx=2)
        
        self.timer_label = tk.Label(timer_frame, 
                                   text="0:00", 
                                   font=("Arial", 12, "bold"),
                                   bg="#e8e8e8",
                                   fg=self.colors['primary'])
        self.timer_label.pack(side=tk.LEFT, padx=2)
        
        # Difficulty score label with icon
        diff_frame = tk.Frame(status_left, bg="#e8e8e8")
        diff_frame.pack(side=tk.LEFT, padx=15)
        
        diff_icon = tk.Label(diff_frame, text="📊", font=("Arial", 12), bg="#e8e8e8")
        diff_icon.pack(side=tk.LEFT, padx=2)
        
        self.difficulty_score_label = tk.Label(diff_frame, 
                                              text="", 
                                              font=("Arial", 10),
                                              bg="#e8e8e8",
                                              fg=self.colors['text'])
        self.difficulty_score_label.pack(side=tk.LEFT, padx=2)
        
        self.metrics_label = tk.Label(self.metrics_frame, 
                                     text="No metrics available",
                                     font=("Arial", 9),
                                     bg=self.colors['bg'],
                                     fg="#666666")
        self.metrics_label.pack(pady=8)
        
        # Create initial board
        self._new_puzzle()
    
    def _on_size_change(self, size_str: str):
        """Handle board size change"""
        if "x" in size_str:
            self.board_size = int(size_str.split("x")[0])
        else:
            self.board_size = 9 # Fallback
        self._new_puzzle()
    
    def _create_board_ui(self):
        """Create the Sudoku board UI"""
        # Clear existing cells
        for widget in self.board_frame.winfo_children():
            widget.destroy()
        self.cells.clear()
        
        # Create grid
        box_size = int(self.board_size ** 0.5)
        # Dynamic sizing
        # Base size for 9x9 is around 600px total width
        total_size = 600
        cell_size = max(25, int(total_size / self.board_size))
        
        # Adjust font size based on cell size
        if self.board_size <= 9: # Single digit
            font_size = int(cell_size * 0.5) 
        else: # Double digit
            font_size = int(cell_size * 0.35)
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                # Create entry with better styling
                entry = tk.Entry(self.board_frame, 
                               width=2 if self.board_size <= 9 else 3, 
                               font=("Arial", font_size, "bold"),
                               justify="center",
                               bg=self.colors['cell_bg'],
                               fg=self.colors['text'],
                               relief=tk.SOLID,
                               borderwidth=1,
                               highlightthickness=2,
                               highlightcolor=self.colors['primary'],
                               highlightbackground=self.colors['border'])
                
                # Calculate padding based on box borders
                padx_val = 2
                pady_val = 2
                
                # Thicker borders for box boundaries
                if row % box_size == 0 and row > 0:
                    pady_val = (4, 2)
                if col % box_size == 0 and col > 0:
                    padx_val = (4, 2)
                
                entry.grid(row=row, column=col, 
                          padx=padx_val, pady=pady_val, 
                          ipadx=2, ipady=4, # Reduced padding for flexibility
                          sticky="nsew")
                
                # Bind events
                entry.bind("<KeyRelease>", lambda e, r=row, c=col: self._on_cell_change(r, c))
                entry.bind("<FocusIn>", lambda e, r=row, c=col: self._on_cell_focus(r, c))
                entry.bind("<Button-1>", lambda e, r=row, c=col: self._on_cell_click(r, c))
                
                # Hover effect
                entry.bind("<Enter>", lambda e, r=row, c=col: self._on_cell_hover(r, c, True))
                entry.bind("<Leave>", lambda e, r=row, c=col: self._on_cell_hover(r, c, False))
                
                self.cells[(row, col)] = entry
        
        # Configure grid weights for better resizing
        for i in range(self.board_size):
            self.board_frame.grid_rowconfigure(i, weight=1)
            self.board_frame.grid_columnconfigure(i, weight=1)
        
        # Update board display
        self._update_board_display()
    
    def _update_board_display(self):
        """Update the board display from current board state"""
        if not self.current_board:
            return
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                value = self.current_board[row, col]
                entry = self.cells[(row, col)]
                
                if value != 0:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(value))
                    
                    # Mark original cells
                    if self.original_board and self.original_board[row, col] != 0:
                        entry.config(state="readonly", bg="#e0e0e0")
                    else:
                        # Keep selected cell highlighted if it's the selected one
                        if self.selected_cell == (row, col):
                            entry.config(state="normal", bg="#ffffcc")
                        else:
                            entry.config(state="normal", bg="white")
                else:
                    entry.delete(0, tk.END)
                    # Keep selected cell highlighted if it's the selected one
                    if self.selected_cell == (row, col):
                        entry.config(state="normal", bg="#ffffcc")
                    else:
                        entry.config(state="normal", bg="white")
        
        # Highlight conflicts (this will override selection color for conflicts)
        self._highlight_conflicts()
    
    def _on_cell_change(self, row: int, col: int):
        """Handle cell value change"""
        entry = self.cells[(row, col)]
        value_str = entry.get().strip()
        
        try:
            if value_str == "":
                value = 0
            else:
                value = int(value_str)
                if value < 1 or value > self.board_size:
                    raise ValueError
            
            # Save to history before change
            self._save_to_history()
            
            self.current_board[row, col] = value
            self._highlight_conflicts()
            
            # Check if solved
            if self.current_board.is_solved():
                self._on_puzzle_solved()
        
        except ValueError:
            entry.delete(0, tk.END)
            if value_str:
                messagebox.showerror("Invalid Input", 
                                    f"Please enter a number between 1 and {self.board_size}")
    
    def _on_cell_hover(self, row: int, col: int, enter: bool):
        """Handle cell hover effect"""
        entry = self.cells[(row, col)]
        if enter and (row, col) != self.selected_cell and (row, col) not in self.conflict_cells:
            if self.original_board and self.original_board[row, col] != 0:
                entry.config(bg="#f0f0f0")
            else:
                entry.config(bg="#f8f8f8")
        elif not enter and (row, col) != self.selected_cell and (row, col) not in self.conflict_cells:
            if self.original_board and self.original_board[row, col] != 0:
                entry.config(bg=self.colors['cell_original'])
            else:
                entry.config(bg=self.colors['cell_bg'])
    
    def _on_cell_click(self, row: int, col: int):
        """Handle cell click - track selected cell"""
        self.selected_cell = (row, col)
        # Highlight selected cell
        for (r, c), entry in self.cells.items():
            if (r, c) == (row, col):
                entry.config(bg=self.colors['cell_selected'],
                           highlightbackground=self.colors['primary'])
            elif (r, c) not in self.conflict_cells:
                if self.original_board and self.original_board[r, c] != 0:
                    entry.config(bg=self.colors['cell_original'],
                               highlightbackground=self.colors['border'])
                else:
                    entry.config(bg=self.colors['cell_bg'],
                               highlightbackground=self.colors['border'])
    
    def _on_cell_focus(self, row: int, col: int):
        """Handle cell focus"""
        self.selected_cell = (row, col)
        # Clear previous highlights
        for (r, c), entry in self.cells.items():
            if (r, c) == (row, col):
                entry.config(bg=self.colors['cell_selected'],
                           highlightbackground=self.colors['primary'])
            elif (r, c) not in self.conflict_cells:
                if self.original_board and self.original_board[r, c] != 0:
                    entry.config(bg=self.colors['cell_original'],
                               highlightbackground=self.colors['border'])
                else:
                    entry.config(bg=self.colors['cell_bg'],
                               highlightbackground=self.colors['border'])
    
    def _highlight_conflicts(self):
        """Highlight conflicting cells"""
        self.conflict_cells.clear()
        
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.current_board[row, col] != 0:
                    conflicts = self.current_board.get_conflicts(row, col)
                    if conflicts:
                        self.conflict_cells.add((row, col))
                        for r, c in conflicts:
                            self.conflict_cells.add((r, c))
        
        # Update colors
        for (row, col), entry in self.cells.items():
            if (row, col) in self.conflict_cells:
                entry.config(bg=self.colors['cell_error'],
                           fg="#cc0000",
                           highlightbackground=self.colors['accent'])
            elif (row, col) == self.selected_cell:
                entry.config(bg=self.colors['cell_selected'],
                           highlightbackground=self.colors['primary'])
    
    def _new_puzzle(self):
        """Generate a new puzzle"""
        try:
            # Get current difficulty from UI (in case it was changed)
            if hasattr(self, 'diff_var'):
                self.difficulty = self.diff_var.get()
            
            if self.board_size == 3:
                self.current_board = self.generator.generate_mini_sudoku(self.difficulty)
            else:
                self.current_board = self.generator.generate(self.board_size, self.difficulty)
            
            self.original_board = self.current_board.copy()
            self.start_time = time.time()
            self.hints_used = 0
            
            # Reset history
            self.history = [self.current_board.copy()]
            self.history_index = 0
            
            # Start timer
            self.timer_running = True
            self._update_timer()
            
            # Calculate difficulty score
            self._update_difficulty_score()
            
            self._create_board_ui()
            self.status_label.config(text="New puzzle generated! Start solving.")
            self.metrics_label.config(text="No metrics available")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate puzzle: {str(e)}")
    
    def _get_hint(self):
        """Get a hint for the selected cell"""
        if not self.current_board:
            messagebox.showinfo("Hint", "Please generate a puzzle first.")
            return
        
        # Use tracked selected cell
        if self.selected_cell is None:
            messagebox.showinfo("Hint", "Please click on an empty cell first, then click Get Hint.")
            return
        
        row, col = self.selected_cell
        
        if self.current_board[row, col] != 0:
            messagebox.showinfo("Hint", "This cell is already filled. Please select an empty cell.")
            return
        
        # Get hint from selected algorithm
        solver = self.solvers[self.selected_algorithm]
        hint = solver.get_hint(self.current_board, row, col)
        
        if hint:
            # Save to history
            self._save_to_history()
            
            self.current_board[row, col] = hint
            self.hints_used += 1
            self._update_board_display()
            self.status_label.config(text=f"Hint: Place {hint} in cell ({row+1}, {col+1}). (Hints used: {self.hints_used})")
            # Keep cell selected
            entry = self.cells[(row, col)]
            entry.config(bg="#ffffcc")
        else:
            messagebox.showinfo("Hint", "No valid hint available for this cell. Try a different cell or algorithm.")
    
    def _solve_puzzle(self):
        """Solve the puzzle using selected algorithm"""
        if not self.current_board:
            return
        
        solver = self.solvers[self.selected_algorithm]
        solved, metrics = solver.solve(self.current_board.copy())
        
        if solved and solved.is_solved():
            # Save to history
            self._save_to_history()
            
            self.current_board = solved
            self._update_board_display()
            self._display_metrics(metrics)
            self.status_label.config(text=f"Puzzle solved using {self.selected_algorithm}!")
            self._on_puzzle_solved()
        else:
            messagebox.showinfo("Solve", 
                              f"Algorithm could not solve this puzzle completely.\n"
                              f"Runtime: {metrics.runtime:.4f}s\n"
                              f"Nodes visited: {metrics.nodes_visited}")
    
    def _compare_algorithms(self):
        """Compare all three algorithms with visual comparison window"""
        if not self.current_board:
            return
        
        # Show loading message
        self.status_label.config(text="🔄 Comparing algorithms... Please wait.")
        self.root.update()
        
        results = {}
        
        for name, solver in self.solvers.items():
            test_board = self.current_board.copy()
            solved, metrics = solver.solve(test_board)
            results[name] = {
                'solved': solved and solved.is_solved() if solved else False,
                'metrics': metrics
            }
        
        # Create visual comparison window
        self._show_comparison_window(results)
        
        # Update metrics display
        best_algo = min(results.items(), 
                       key=lambda x: x[1]['metrics'].runtime if x[1]['solved'] else float('inf'))
        if best_algo[1]['solved']:
            self._display_metrics(best_algo[1]['metrics'])
            self.status_label.config(text=f"🏆 Best algorithm: {best_algo[0]}")
        else:
            self.status_label.config(text="Comparison completed.")
    
    def _show_comparison_window(self, results: Dict):
        """Show visual comparison window with tables and colors"""
        # Create new window
        comp_window = tk.Toplevel(self.root)
        comp_window.title("📊 Algorithm Comparison")
        comp_window.geometry("950x650")
        comp_window.configure(bg="#f5f5f5")
        comp_window.transient(self.root)
        comp_window.grab_set()
        
        # Center the comparison window
        comp_window.update_idletasks()
        x = (comp_window.winfo_screenwidth() // 2) - (950 // 2)
        y = (comp_window.winfo_screenheight() // 2) - (650 // 2)
        comp_window.geometry(f"950x650+{x}+{y}")
        
        # Title
        title_frame = tk.Frame(comp_window, bg=self.colors['primary'], height=70)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame,
                              text="📊 Algorithm Performance Comparison",
                              font=("Arial", 18, "bold"),
                              bg=self.colors['primary'],
                              fg="white")
        title_label.pack(pady=20)
        
        # Main content frame with padding
        content_frame = tk.Frame(comp_window, bg="#f5f5f5", padx=25, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create modern table with shadow effect
        table_container = tk.Frame(content_frame, bg="#e0e0e0")
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        table_frame = tk.Frame(table_container, bg="white", relief=tk.FLAT, borderwidth=0)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Table headers with better styling
        headers = ["Algorithm", "Status", "Runtime", "Nodes", "Backtracks", "Domain Reductions"]
        header_frame = tk.Frame(table_frame, bg="#2c3e50", height=45)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Header labels - all centered for alignment
        for i, header in enumerate(headers):
            header_label = tk.Label(header_frame,
                                  text=header,
                                  font=("Arial", 11, "bold"),
                                  bg="#2c3e50",
                                  fg="white",
                                  anchor="center",
                                  padx=15,
                                  pady=12)
            header_label.grid(row=0, column=i, sticky="ew", padx=0)
        
        # Configure header columns - Algorithm column wider
        header_frame.grid_columnconfigure(0, weight=3)  # Algorithm column
        for i in range(1, 6):
            header_frame.grid_columnconfigure(i, weight=2)  # Other columns
        
        # Algorithm rows with alternating colors
        algo_colors = {
            "Constraint Propagation": {"bg": "#e8f4f8", "border": "#b3d9e6"},
            "AC-3": {"bg": "#f0f8e8", "border": "#c8e6c9"},
            "Backtracking": {"bg": "#fff8e1", "border": "#ffe082"}
        }
        
        row_num = 0
        best_runtime = float('inf')
        best_algo_name = None
        
        # Find best runtime
        for name, result in results.items():
            if result['solved'] and result['metrics'].runtime < best_runtime:
                best_runtime = result['metrics'].runtime
                best_algo_name = name
        
        for name, result in results.items():
            m = result['metrics']
            algo_color = algo_colors.get(name, {"bg": "#ffffff", "border": "#e0e0e0"})
            
            # Row frame with border
            row_frame = tk.Frame(table_frame, 
                                bg=algo_color["bg"], 
                                relief=tk.FLAT,
                                borderwidth=0,
                                height=60)
            row_frame.pack(fill=tk.X, padx=0, pady=1)
            row_frame.pack_propagate(False)
            
            # Highlight best algorithm row
            if name == best_algo_name and result['solved']:
                row_frame.configure(bg="#fffde7", relief=tk.SOLID, borderwidth=2)
            
            # Algorithm name (bold, centered for alignment)
            name_label = tk.Label(row_frame,
                                text=name,
                                font=("Arial", 11, "bold"),
                                bg=row_frame.cget("bg"),
                                fg="#1a1a1a",
                                anchor="center",
                                padx=15,
                                pady=15)
            name_label.grid(row=0, column=0, sticky="ew")
            
            # Status (with icon and color)
            if result['solved']:
                status_text = "✅ Solved"
                status_color = "#2e7d32"
            else:
                status_text = "❌ Failed"
                status_color = "#c62828"
            
            status_label = tk.Label(row_frame,
                                   text=status_text,
                                   font=("Arial", 10, "bold"),
                                   bg=row_frame.cget("bg"),
                                   fg=status_color,
                                   anchor="center",
                                   padx=15,
                                   pady=15)
            status_label.grid(row=0, column=1, sticky="ew")
            
            # Runtime (highlight best with trophy)
            runtime_text = f"{m.runtime:.4f}s"
            if name == best_algo_name and result['solved']:
                runtime_text = f"🏆 {runtime_text}"
                runtime_fg = "#1976d2"
                runtime_font = ("Arial", 10, "bold")
            else:
                runtime_fg = "#424242"
                runtime_font = ("Arial", 10)
            
            runtime_label = tk.Label(row_frame,
                                   text=runtime_text,
                                   font=runtime_font,
                                   bg=row_frame.cget("bg"),
                                   fg=runtime_fg,
                                   anchor="center",
                                   padx=15,
                                   pady=15)
            runtime_label.grid(row=0, column=2, sticky="ew")
            
            # Nodes visited (formatted with commas)
            nodes_label = tk.Label(row_frame,
                                 text=f"{m.nodes_visited:,}",
                                 font=("Arial", 10),
                                 bg=row_frame.cget("bg"),
                                 fg="#424242",
                                 anchor="center",
                                 padx=15,
                                 pady=15)
            nodes_label.grid(row=0, column=3, sticky="ew")
            
            # Backtracks
            backtracks_label = tk.Label(row_frame,
                                      text=f"{m.backtrack_count:,}",
                                      font=("Arial", 10),
                                      bg=row_frame.cget("bg"),
                                      fg="#424242",
                                      anchor="center",
                                      padx=15,
                                      pady=15)
            backtracks_label.grid(row=0, column=4, sticky="ew")
            
            # Domain reductions
            reductions_label = tk.Label(row_frame,
                                      text=f"{m.domain_reductions:,}",
                                      font=("Arial", 10),
                                      bg=row_frame.cget("bg"),
                                      fg="#424242",
                                      anchor="center",
                                      padx=15,
                                      pady=15)
            reductions_label.grid(row=0, column=5, sticky="ew")
            
            # Configure grid weights (same as header) - all columns properly aligned
            row_frame.grid_columnconfigure(0, weight=3)  # Algorithm column
            for i in range(1, 6):
                row_frame.grid_columnconfigure(i, weight=2)  # Other columns
            
            row_num += 1
        
        # Summary frame with modern design
        summary_frame = tk.Frame(content_frame, 
                                bg="#ffffff", 
                                relief=tk.FLAT,
                                borderwidth=1)
        summary_frame.pack(fill=tk.X, pady=(20, 10))
        
        summary_inner = tk.Frame(summary_frame, bg="#f8f9fa", relief=tk.FLAT)
        summary_inner.pack(fill=tk.X, padx=2, pady=2)
        
        summary_text = "📈 Summary: "
        if best_algo_name:
            best_metrics = results[best_algo_name]['metrics']
            summary_text += f"🏆 {best_algo_name} is fastest ({best_metrics.runtime:.4f}s)"
            summary_color = "#1976d2"
        else:
            summary_text += "No algorithm solved the puzzle completely."
            summary_color = "#757575"
        
        summary_label = tk.Label(summary_inner,
                                text=summary_text,
                                font=("Arial", 12, "bold"),
                                bg="#f8f9fa",
                                fg=summary_color,
                                padx=20,
                                pady=15)
        summary_label.pack()
        
        # Close button with modern style
        button_frame = tk.Frame(content_frame, bg="#f5f5f5")
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        close_btn = tk.Button(button_frame,
                            text="✓ Close",
                            font=("Arial", 11, "bold"),
                            bg=self.colors['primary'],
                            fg="white",
                            activebackground="#357abd",
                            activeforeground="white",
                            relief=tk.FLAT,
                            padx=40,
                            pady=12,
                            cursor="hand2",
                            borderwidth=0,
                            highlightthickness=0,
                            command=comp_window.destroy)
        close_btn.pack()
        
        # Hover effect for button
        def on_enter(e):
            close_btn.config(bg="#5aa0f0")
        
        def on_leave(e):
            close_btn.config(bg=self.colors['primary'])
        
        close_btn.bind("<Enter>", on_enter)
        close_btn.bind("<Leave>", on_leave)
    
    def _display_metrics(self, metrics: AlgorithmMetrics):
        """Display algorithm metrics"""
        text = (f"Runtime: {metrics.runtime:.4f}s | "
                f"Nodes: {metrics.nodes_visited} | "
                f"Backtracks: {metrics.backtrack_count} | "
                f"Domain reductions: {metrics.domain_reductions}")
        self.metrics_label.config(text=text)
    
    def _clear_board(self):
        """Clear user-entered values"""
        if not self.current_board or not self.original_board:
            return
        
        # Save to history
        self._save_to_history()
        
        self.current_board = self.original_board.copy()
        self.hints_used = 0
        self._update_board_display()
        self.status_label.config(text="Board cleared to original state.")
    
    def _check_solution(self):
        """Check if current solution is correct"""
        if not self.current_board:
            return
        
        if not self.current_board.is_complete():
            messagebox.showinfo("Check", "Puzzle is not complete yet.")
            return
        
        if self.current_board.is_solved():
            elapsed = time.time() - self.start_time if self.start_time else 0
            messagebox.showinfo("Congratulations!", 
                              f"Puzzle solved correctly!\n"
                              f"Time: {elapsed:.1f}s\n"
                              f"Hints used: {self.hints_used}")
        else:
            conflicts = []
            for row in range(self.board_size):
                for col in range(self.board_size):
                    if not self.current_board.is_valid_move(row, col, self.current_board[row, col]):
                        conflicts.append(f"Cell ({row+1}, {col+1})")
            
            messagebox.showerror("Incorrect", 
                               f"Solution has errors:\n" + "\n".join(conflicts[:10]))
    
    def _on_puzzle_solved(self):
        """Handle puzzle solved event"""
        if self.start_time:
            elapsed = time.time() - self.start_time
            self.timer_running = False
            
            # Update statistics
            self.stats['puzzles_solved'] += 1
            self.stats['total_time'] += elapsed
            self.stats['total_hints'] += self.hints_used
            if elapsed < self.stats['best_time']:
                self.stats['best_time'] = elapsed
            
            self.status_label.config(
                text=f"🎉 Puzzle solved! Time: {elapsed:.1f}s, Hints: {self.hints_used}"
            )
            
            # Show congratulations
            avg_time = self.stats['total_time'] / self.stats['puzzles_solved']
            messagebox.showinfo("Congratulations!", 
                              f"Puzzle solved correctly!\n\n"
                              f"Time: {elapsed:.1f}s\n"
                              f"Hints used: {self.hints_used}\n\n"
                              f"Total puzzles solved: {self.stats['puzzles_solved']}\n"
                              f"Average time: {avg_time:.1f}s")
    
    def _save_to_history(self):
        """Save current board state to history"""
        board_copy = self.current_board.copy()
        
        # Remove any future history if we're not at the end
        if self.history_index < len(self.history) - 1:
            self.history = self.history[:self.history_index + 1]
        
        # Add new state
        self.history.append(board_copy)
        self.history_index += 1
        
        # Limit history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
            self.history_index -= 1
    
    def _undo_move(self):
        """Undo last move"""
        if self.history_index > 0:
            self.history_index -= 1
            self.current_board = self.history[self.history_index].copy()
            self._update_board_display()
            self.status_label.config(text="Move undone. (Ctrl+Z)")
    
    def _redo_move(self):
        """Redo last undone move"""
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            self.current_board = self.history[self.history_index].copy()
            self._update_board_display()
            self.status_label.config(text="Move redone. (Ctrl+Y)")
    
    def _update_timer(self):
        """Update timer display"""
        if self.timer_running and self.start_time:
            elapsed = time.time() - self.start_time
            minutes = int(elapsed // 60)
            seconds = int(elapsed % 60)
            self.timer_label.config(text=f"Time: {minutes}:{seconds:02d}")
            self.timer_id = self.root.after(1000, self._update_timer)
        else:
            if self.timer_id:
                self.root.after_cancel(self.timer_id)
    
    def _on_difficulty_change(self, event=None):
        """Handle difficulty selection change"""
        new_difficulty = self.diff_var.get()
        self.difficulty = new_difficulty
        # Update display if puzzle exists
        if self.current_board:
            self._update_difficulty_score()
    
    def _update_difficulty_score(self):
        """Calculate and display puzzle difficulty score"""
        if not self.current_board:
            return
        
        # Get selected difficulty (what user chose)
        selected_difficulty = self.difficulty.capitalize()
        
        # Calculate actual puzzle difficulty based on filled cells
        empty_cells = len(self.current_board.get_empty_cells())
        total_cells = self.board_size * self.board_size
        filled_cells = total_cells - empty_cells
        filled_ratio = filled_cells / total_cells  # Ratio of filled cells
        
        # Calculate difficulty score (0-100)
        # LESS filled cells = HARDER puzzle = HIGHER score
        # Easy: 50%+ filled (0.5-1.0) -> score 0-40
        # Medium: 35-50% filled (0.35-0.5) -> score 40-70
        # Hard: 25-35% filled (0.25-0.35) -> score 70-100
        
        # Calculate difficulty score (0-100)
        # LESS filled cells = HARDER puzzle = HIGHER score
        # Easy: 45%+ filled -> score 0-40
        # Medium: 30-45% filled -> score 40-70  
        # Hard: 20-30% filled -> score 70-100
        
        if filled_ratio >= 0.45:  # 45%+ filled = Easy
            # Map 0.45-1.0 to 40-0 (more filled = easier = lower score)
            # filled_ratio = 0.45 -> score = 40
            # filled_ratio = 1.0 -> score = 0
            score = int(40 - (filled_ratio - 0.45) / 0.55 * 40)
            calculated_level = "Easy"
        elif filled_ratio >= 0.30:  # 30-45% filled = Medium
            # Map 0.30-0.45 to 70-40
            # filled_ratio = 0.45 -> score = 40
            # filled_ratio = 0.30 -> score = 70
            score = int(40 + (0.45 - filled_ratio) / 0.15 * 30)
            calculated_level = "Medium"
        else:  # < 30% filled = Hard
            # Map 0.20-0.30 to 100-70
            # filled_ratio = 0.30 -> score = 70
            # filled_ratio = 0.20 -> score = 100
            if filled_ratio < 0.20:
                filled_ratio = 0.20  # Cap at 20%
            score = int(70 + (0.30 - filled_ratio) / 0.10 * 30)
            calculated_level = "Hard"
        
        # Ensure score is in valid range
        score = max(0, min(100, score))
        
        # Show selected difficulty (what user chose) - this is what matters
        # The score shows the actual puzzle difficulty based on filled cells
        self.difficulty_score_label.config(
            text=f"Difficulty: {selected_difficulty} | Score: {score}/100"
        )
    
    def _animate_hint(self, row: int, col: int):
        """Animate hint cell"""
        entry = self.cells[(row, col)]
        original_bg = entry.cget('bg')
        
        # Flash animation
        def flash(count=0):
            if count < 3:
                if count % 2 == 0:
                    entry.config(bg=self.colors['secondary'])
                else:
                    entry.config(bg=self.colors['cell_hint'])
                self.root.after(150, lambda: flash(count + 1))
        
        flash()
    
    def _show_stats(self):
        """Show statistics window"""
        if self.stats['puzzles_solved'] == 0:
            messagebox.showinfo("📊 Statistics", 
                              "No puzzles solved yet! 🎯\n\n"
                              "Solve a puzzle to see your statistics.")
            return
        
        avg_time = self.stats['total_time'] / self.stats['puzzles_solved']
        avg_hints = self.stats['total_hints'] / self.stats['puzzles_solved']
        best_time_str = f"{self.stats['best_time']:.1f}s" if self.stats['best_time'] != float('inf') else "N/A"
        
        stats_text = (
            f"📊 Game Statistics\n"
            f"{'='*30}\n\n"
            f"✅ Puzzles Solved: {self.stats['puzzles_solved']}\n"
            f"⏱️  Total Time: {self.stats['total_time']:.1f}s\n"
            f"📈 Average Time: {avg_time:.1f}s\n"
            f"🏆 Best Time: {best_time_str}\n"
            f"💡 Total Hints Used: {self.stats['total_hints']}\n"
            f"📊 Average Hints: {avg_hints:.1f}\n"
        )
        
        messagebox.showinfo("📊 Statistics", stats_text)


    def _center_window(self, width: int, height: int):
        """Center the window on the screen"""
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Calculate position to center
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        # Set geometry with centered position
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Bind resize event to keep content responsive
        self.root.bind('<Configure>', self._on_window_resize)
    
    def _on_window_resize(self, event=None):
        """Handle window resize to keep content responsive"""
        # Update layout on resize to maintain centering
        if event and event.widget == self.root:
            self.root.update_idletasks()
    
    # ==================== Animation Methods ====================
    
    def _create_animation_controls(self):
        """Create animation control panel"""
        # Animation controls (initially hidden)
        self.animation_controls = tk.Frame(self.animation_frame, bg="#fff3e0")
        self.animation_controls.pack(fill=tk.X, padx=10, pady=8)
        
        # Play/Pause button
        self.play_pause_btn = tk.Button(self.animation_controls, 
                                        text="⏸️ Pause",
                                        font=("Arial", 10, "bold"),
                                        bg="#ff9800", fg="white",
                                        command=self._toggle_animation,
                                        relief=tk.FLAT, padx=15, pady=5)
        self.play_pause_btn.pack(side=tk.LEFT, padx=5)
        
        # Stop button
        tk.Button(self.animation_controls, 
                 text="⏹️ Stop",
                 font=("Arial", 10),
                 bg="#f44336", fg="white",
                 command=self._stop_animation,
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Step button
        tk.Button(self.animation_controls, 
                 text="⏭️ Step",
                 font=("Arial", 10),
                 bg="#2196f3", fg="white",
                 command=self._step_animation,
                 relief=tk.FLAT, padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        # Speed label
        tk.Label(self.animation_controls, text="Speed:", 
                font=("Arial", 10), bg="#fff3e0").pack(side=tk.LEFT, padx=(20, 5))
        
        # Speed slider
        self.speed_var = tk.IntVar(value=200)
        self.speed_slider = tk.Scale(self.animation_controls,
                                    from_=10, to=500,
                                    orient=tk.HORIZONTAL,
                                    variable=self.speed_var,
                                    length=150,
                                    bg="#fff3e0",
                                    highlightthickness=0,
                                    command=self._on_speed_change)
        self.speed_slider.pack(side=tk.LEFT, padx=5)
        
        # Speed label (ms)
        self.speed_label = tk.Label(self.animation_controls, text="200ms", 
                                   font=("Arial", 9), bg="#fff3e0")
        self.speed_label.pack(side=tk.LEFT, padx=5)
        
        # Animation status
        self.animation_status = tk.Label(self.animation_controls, 
                                        text="",
                                        font=("Arial", 10),
                                        bg="#fff3e0", fg="#424242")
        self.animation_status.pack(side=tk.RIGHT, padx=10)
    
    def _on_speed_change(self, value):
        """Handle speed slider change"""
        speed = int(value)
        self.speed_label.config(text=f"{speed}ms")
        self.animation.set_speed_ms(speed)
    
    def _solve_animated(self):
        """Start animated solving"""
        if not self.current_board:
            messagebox.showinfo("Animation", "Please generate a puzzle first.")
            return
        
        if self.animation.is_playing() or self.animation.is_paused():
            messagebox.showinfo("Animation", "Animation already running. Stop it first.")
            return
        
        # Show animation controls
        self.animation_frame.pack(fill=tk.X, pady=5)
        
        # Save board state for animation
        self.animation_board = self.current_board.copy()
        
        # Get solver
        solver = self.solvers[self.selected_algorithm]
        
        # Check if solver has solve_with_steps
        if not hasattr(solver, 'solve_with_steps'):
            messagebox.showerror("Animation", 
                               f"Algorithm '{self.selected_algorithm}' doesn't support step animation.")
            return
        
        # Start animation
        step_generator = solver.solve_with_steps(self.animation_board)
        self.animation.set_speed_ms(self.speed_var.get())
        self.animation.start(step_generator)
        
        self.status_label.config(text="🎬 Animation started... Press Space to pause/resume, Esc to stop")
        self.play_pause_btn.config(text="⏸️ Pause")
        
        # Start animation loop
        self._run_animation_step()
    
    def _run_animation_step(self):
        """Execute one animation step"""
        if not self.animation.is_playing():
            return
        
        step = self.animation.step_forward()
        
        if step and self.animation.should_continue():
            # Schedule next step
            delay = self.animation.get_delay_ms()
            self.animation_timer_id = self.root.after(delay, self._run_animation_step)
    
    def _on_animation_step(self, step: SolveStep, index: int):
        """Handle animation step - update UI"""
        # Update animation status
        self.animation_status.config(text=f"Step {index + 1}: {step.message}")
        
        # Get color based on step type
        if step.step_type == StepType.ASSIGN:
            color = self.colors['cell_assign']
        elif step.step_type == StepType.TRY:
            color = self.colors['cell_try']
        elif step.step_type == StepType.BACKTRACK:
            color = self.colors['cell_backtrack']
        elif step.step_type == StepType.PROPAGATE:
            color = self.colors['cell_propagate']
        elif step.step_type == StepType.REVISE:
            color = self.colors['cell_revise']
        else:
            color = self.colors['cell_bg']
        
        # Update cell if valid position
        if 0 <= step.row < self.board_size and 0 <= step.col < self.board_size:
            entry = self.cells.get((step.row, step.col))
            if entry:
                entry.config(bg=color)
                
                # Update value
                if step.value is not None:
                    entry.delete(0, tk.END)
                    if step.step_type != StepType.BACKTRACK:
                        entry.insert(0, str(step.value))
                
                # Flash effect - return to normal after a short delay
                if step.step_type in (StepType.ASSIGN, StepType.PROPAGATE):
                    self.root.after(100, lambda r=step.row, c=step.col: 
                                   self._reset_cell_color(r, c))
    
    def _reset_cell_color(self, row: int, col: int):
        """Reset cell to normal color"""
        if (row, col) in self.cells:
            entry = self.cells[(row, col)]
            if self.original_board and self.original_board[row, col] != 0:
                entry.config(bg=self.colors['cell_original'])
            else:
                entry.config(bg=self.colors['cell_bg'])
    
    def _on_animation_state_change(self, state: AnimationState):
        """Handle animation state change"""
        if state == AnimationState.PAUSED:
            self.play_pause_btn.config(text="▶️ Resume")
            self.status_label.config(text="⏸️ Animation paused")
        elif state == AnimationState.PLAYING:
            self.play_pause_btn.config(text="⏸️ Pause")
            self.status_label.config(text="🎬 Animation running...")
        elif state == AnimationState.STOPPED:
            self._cleanup_animation()
    
    def _on_animation_finished(self, success: bool):
        """Handle animation completion"""
        if success:
            self.current_board = self.animation_board
            self._update_board_display()
            self.status_label.config(text="✅ Animation complete - Puzzle solved!")
            self._on_puzzle_solved()
        else:
            self.status_label.config(text="❌ Animation complete - No solution found")
        
        self._cleanup_animation()
    
    def _toggle_animation(self):
        """Toggle animation pause/resume"""
        if self.animation.is_playing():
            self.animation.pause()
            if self.animation_timer_id:
                self.root.after_cancel(self.animation_timer_id)
        elif self.animation.is_paused():
            self.animation.resume()
            self._run_animation_step()
    
    def _stop_animation(self):
        """Stop animation"""
        if self.animation.is_playing() or self.animation.is_paused():
            self.animation.stop()
            if self.animation_timer_id:
                self.root.after_cancel(self.animation_timer_id)
            self._cleanup_animation()
    
    def _step_animation(self):
        """Execute single animation step"""
        if self.animation.is_paused():
            self.animation.step_forward()
    
    def _cleanup_animation(self):
        """Clean up animation state"""
        self.animation_frame.pack_forget()
        self.animation.reset()
        self.animation_board = None
        if self.animation_timer_id:
            self.root.after_cancel(self.animation_timer_id)
            self.animation_timer_id = None
    



def main():
    """Main entry point"""
    root = tk.Tk()
    game = SudokuGame(root)
    root.mainloop()


if __name__ == "__main__":
    main()

