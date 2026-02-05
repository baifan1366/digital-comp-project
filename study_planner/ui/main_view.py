"""
Main application window for the Study Planner.

Provides the primary user interface with preset plan selection,
custom plan configuration, history display, and session controls.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List
from study_planner.core.plans import StudyPlan, PlanManager
from study_planner.data.history import HistoryManager
from study_planner.data.statistics import StatisticsTracker
from study_planner.utils.validation import validate_numeric_input
from study_planner.utils.time_utils import format_duration


class MainWindow:
    """
    Main application window for Study Planner.
    
    Provides UI for:
    - Preset plan selection (Pomodoro, Deep Focus, Light Review)
    - Custom plan configuration with validation
    - History display with clickable recent configurations
    - Session control buttons (start/pause/resume/stop)
    """
    
    def __init__(
        self,
        root,
        plan_manager: PlanManager,
        history_manager: HistoryManager,
        statistics_tracker: Optional[StatisticsTracker] = None
    ):
        """
        Initialize the main window.
        
        Args:
            root: Tkinter root window or Frame
            plan_manager: PlanManager instance for plan operations
            history_manager: HistoryManager instance for history operations
            statistics_tracker: Optional StatisticsTracker instance for statistics display
        """
        self.root = root
        self.plan_manager = plan_manager
        self.history_manager = history_manager
        self.statistics_tracker = statistics_tracker
        
        # Current selected plan
        self._selected_plan: Optional[StudyPlan] = None
        
        # Callbacks for session control
        self._on_start_callback: Optional[Callable[[StudyPlan], None]] = None
        self._on_pause_callback: Optional[Callable[[], None]] = None
        self._on_resume_callback: Optional[Callable[[], None]] = None
        self._on_stop_callback: Optional[Callable[[], None]] = None
        
        # UI state
        self._session_active = False
        self._session_paused = False
        
        # Setup window if root is Tk instance
        if isinstance(self.root, tk.Tk):
            self.root.title("Study Planner")
            self.root.geometry("600x800")
            self.root.resizable(False, False)
        
        # Build UI
        self._build_ui()