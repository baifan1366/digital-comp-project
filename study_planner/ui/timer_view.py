"""
Timer display component for the Study Planner.

Provides a visual countdown timer with state indicator and cycle progress.
"""

import tkinter as tk
from tkinter import ttk
from study_planner.core.state import SessionState
from study_planner.utils.time_utils import format_time


class TimerDisplay:
    """
    Timer display widget showing countdown and session information.
    
    Displays:
    - MM:SS countdown timer
    - Current state (Study, Break, Long Break)
    - Cycle progress (e.g., "Cycle 2 of 4")
    """
    
    def __init__(self, parent: tk.Widget):
        """
        Initialize the timer display.
        
        Args:
            parent: Parent Tkinter widget
        """
        self.parent = parent
        
        # Create main frame
        self.frame = ttk.Frame(parent, padding="20")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Build UI components
        self._build_ui()
        
        # Initialize display
        self.update_time(0)
        self.update_state(SessionState.IDLE)
        self.update_cycle(0, 0)
    
    def _build_ui(self) -> None:
        """Build the timer display UI components."""
        # State label (Study, Break, Long Break)
        self.state_label = ttk.Label(
            self.frame,
            text="Ready",
            font=("Arial", 16, "bold"),
            anchor=tk.CENTER
        )
        self.state_label.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Timer display (MM:SS)
        self.timer_label = ttk.Label(
            self.frame,
            text="00:00",
            font=("Arial", 48, "bold"),
            anchor=tk.CENTER
        )
        self.timer_label.grid(row=1, column=0, pady=20, sticky=(tk.W, tk.E))
        
        # Cycle progress label
        self.cycle_label = ttk.Label(
            self.frame,
            text="",
            font=("Arial", 12),
            anchor=tk.CENTER
        )
        self.cycle_label.grid(row=2, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Configure column to expand
        self.frame.columnconfigure(0, weight=1)
    
    def update_time(self, remaining_seconds: int) -> None:
        """
        Update the countdown timer display.
        
        Args:
            remaining_seconds: Seconds remaining in current phase
        """
        time_str = format_time(remaining_seconds)
        self.timer_label.config(text=time_str)
    
    def update_state(self, state: SessionState) -> None:
        """
        Update the current state indicator.
        
        Args:
            state: Current SessionState
        """
        state_text_map = {
            SessionState.IDLE: "Ready",
            SessionState.STUDY: "Study Time",
            SessionState.BREAK: "Break Time",
            SessionState.LONG_BREAK: "Long Break",
            SessionState.PAUSED: "Paused",
            SessionState.COMPLETED: "Session Complete"
        }
        
        state_color_map = {
            SessionState.IDLE: "black",
            SessionState.STUDY: "green",
            SessionState.BREAK: "blue",
            SessionState.LONG_BREAK: "purple",
            SessionState.PAUSED: "orange",
            SessionState.COMPLETED: "gray"
        }
        
        text = state_text_map.get(state, "Unknown")
        color = state_color_map.get(state, "black")
        
        self.state_label.config(text=text, foreground=color)
    
    def update_cycle(self, current_cycle: int, total_cycles: int) -> None:
        """
        Update the cycle progress indicator.
        
        Args:
            current_cycle: Current cycle number (1-indexed)
            total_cycles: Total number of cycles
        """
        if total_cycles > 1 and current_cycle > 0:
            cycle_text = f"Cycle {current_cycle} of {total_cycles}"
        elif total_cycles == 1 and current_cycle > 0:
            cycle_text = "Single Cycle Session"
        else:
            cycle_text = ""
        
        self.cycle_label.config(text=cycle_text)
    
    def get_frame(self) -> ttk.Frame:
        """
        Get the main frame widget.
        
        Returns:
            The timer display frame
        """
        return self.frame
