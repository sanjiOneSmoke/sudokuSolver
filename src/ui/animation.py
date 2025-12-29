"""
Animation Controller for Step-by-Step Sudoku Solving
Handles animation timing, pause/resume, and step management
"""

import time
from typing import Generator, Optional, Callable, List
from dataclasses import dataclass
from enum import Enum
from src.solvers.base import SolveStep, StepType


class AnimationState(Enum):
    """Current state of the animation"""
    IDLE = "idle"
    PLAYING = "playing"
    PAUSED = "paused"
    STOPPED = "stopped"
    FINISHED = "finished"


class AnimationSpeed(Enum):
    """Animation speed presets"""
    SLOW = 500      # 500ms per step
    NORMAL = 200    # 200ms per step
    FAST = 50       # 50ms per step
    INSTANT = 0     # No delay


@dataclass
class AnimationSettings:
    """Settings for animation playback"""
    speed: AnimationSpeed = AnimationSpeed.NORMAL
    skip_try_steps: bool = False  # Skip "TRY" steps for faster visualization
    highlight_duration: int = 100  # How long to highlight a cell (ms)


class AnimationController:
    """
    Controls the step-by-step solving animation.
    Works with any solver that has solve_with_steps method.
    """
    
    def __init__(self):
        self.state = AnimationState.IDLE
        self.settings = AnimationSettings()
        self.steps: List[SolveStep] = []
        self.current_step_index = 0
        self.step_generator: Optional[Generator] = None
        
        # Callbacks
        self.on_step: Optional[Callable[[SolveStep, int], None]] = None
        self.on_state_change: Optional[Callable[[AnimationState], None]] = None
        self.on_finished: Optional[Callable[[bool], None]] = None
        
        # For pause/resume
        self._pause_requested = False
        self._stop_requested = False
    
    def set_speed(self, speed: AnimationSpeed):
        """Set animation speed"""
        self.settings.speed = speed
    
    def set_speed_ms(self, delay_ms: int):
        """Set custom animation speed in milliseconds"""
        # Create custom speed by closest match
        if delay_ms >= 400:
            self.settings.speed = AnimationSpeed.SLOW
        elif delay_ms >= 100:
            self.settings.speed = AnimationSpeed.NORMAL
        elif delay_ms >= 20:
            self.settings.speed = AnimationSpeed.FAST
        else:
            self.settings.speed = AnimationSpeed.INSTANT
        # Store actual value for custom speeds
        self._custom_delay = delay_ms
    
    def get_delay_ms(self) -> int:
        """Get current delay in milliseconds"""
        if hasattr(self, '_custom_delay'):
            return self._custom_delay
        return self.settings.speed.value
    
    def start(self, step_generator: Generator):
        """
        Start animation with given step generator.
        
        Args:
            step_generator: Generator from solver.solve_with_steps()
        """
        self.step_generator = step_generator
        self.steps = []
        self.current_step_index = 0
        self._pause_requested = False
        self._stop_requested = False
        self._set_state(AnimationState.PLAYING)
    
    def pause(self):
        """Pause the animation"""
        if self.state == AnimationState.PLAYING:
            self._pause_requested = True
            self._set_state(AnimationState.PAUSED)
    
    def resume(self):
        """Resume paused animation"""
        if self.state == AnimationState.PAUSED:
            self._pause_requested = False
            self._set_state(AnimationState.PLAYING)
    
    def stop(self):
        """Stop the animation completely"""
        self._stop_requested = True
        self._set_state(AnimationState.STOPPED)
    
    def step_forward(self) -> Optional[SolveStep]:
        """
        Execute single step forward.
        Returns the step that was executed, or None if finished.
        """
        if self.step_generator is None:
            return None
        
        try:
            step = next(self.step_generator)
            self.steps.append(step)
            self.current_step_index = len(self.steps) - 1
            
            if self.on_step:
                self.on_step(step, self.current_step_index)
            
            if step.step_type == StepType.SOLVED:
                self._set_state(AnimationState.FINISHED)
                if self.on_finished:
                    self.on_finished(True)
            elif step.step_type == StepType.FAILED:
                self._set_state(AnimationState.FINISHED)
                if self.on_finished:
                    self.on_finished(False)
            
            return step
            
        except StopIteration:
            self._set_state(AnimationState.FINISHED)
            if self.on_finished:
                self.on_finished(False)
            return None
    
    def should_skip_step(self, step: SolveStep) -> bool:
        """Check if step should be skipped based on settings"""
        if self.settings.skip_try_steps and step.step_type == StepType.TRY:
            return True
        return False
    
    def is_playing(self) -> bool:
        """Check if animation is currently playing"""
        return self.state == AnimationState.PLAYING
    
    def is_paused(self) -> bool:
        """Check if animation is paused"""
        return self.state == AnimationState.PAUSED
    
    def is_finished(self) -> bool:
        """Check if animation has finished"""
        return self.state == AnimationState.FINISHED
    
    def is_stopped(self) -> bool:
        """Check if animation was stopped"""
        return self.state == AnimationState.STOPPED
    
    def should_continue(self) -> bool:
        """Check if animation should continue (not paused or stopped)"""
        return not self._pause_requested and not self._stop_requested
    
    def get_statistics(self) -> dict:
        """Get animation statistics"""
        step_counts = {st: 0 for st in StepType}
        for step in self.steps:
            step_counts[step.step_type] += 1
        
        return {
            'total_steps': len(self.steps),
            'current_step': self.current_step_index,
            'step_counts': step_counts,
            'state': self.state.value
        }
    
    def reset(self):
        """Reset controller to initial state"""
        self.state = AnimationState.IDLE
        self.steps = []
        self.current_step_index = 0
        self.step_generator = None
        self._pause_requested = False
        self._stop_requested = False
        if hasattr(self, '_custom_delay'):
            delattr(self, '_custom_delay')
    
    def _set_state(self, new_state: AnimationState):
        """Set state and notify listeners"""
        old_state = self.state
        self.state = new_state
        if self.on_state_change and old_state != new_state:
            self.on_state_change(new_state)
