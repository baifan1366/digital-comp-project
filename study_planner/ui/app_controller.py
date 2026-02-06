"""
Application controller for integrating UI with core logic.

Provides thread-safe integration between Tkinter UI and the StudyPlanner
core logic, handling callbacks and state synchronization.
"""

import tkinter as tk
from queue import Queue
from typing import Optional
from study_planner.core.planner import StudyPlanner
from study_planner.core.plans import StudyPlan, PlanManager
from study_planner.core.state import SessionState
from study_planner.data.history import HistoryManager
from study_planner.data.statistics import StatisticsTracker
from study_planner.core.notifier import Notifier
from study_planner.ui.navigation_view import NavigationView
from study_planner.ui.timer_view import TimerDisplay
from study_planner.ui.dialogs import NotificationPopup


class AppController:
    """
    Controller for integrating UI with core study planner logic.
    
    Manages:
    - Thread-safe communication between timer callbacks and UI updates
    - Session state synchronization
    - Configuration modification prevention during active sessions
    - Notification delivery through UI popups
    """
    
    def __init__(
        self,
        root: tk.Tk,
        planner: StudyPlanner,
        plan_manager: PlanManager,
        history_manager: HistoryManager,
        statistics_tracker: StatisticsTracker,
        notifier: Notifier
    ):
        """
        Initialize the application controller.
        
        Args:
            root: Tkinter root window
            planner: StudyPlanner instance
            plan_manager: PlanManager instance
            history_manager: HistoryManager instance
            statistics_tracker: StatisticsTracker instance
            notifier: Notifier instance
        """
        self.root = root
        self.planner = planner
        self.plan_manager = plan_manager
        self.history_manager = history_manager
        self.statistics_tracker = statistics_tracker
        self.notifier = notifier
        
        # Thread-safe queue for UI updates
        self.ui_queue: Queue = Queue()
        
        # Create UI components
        self._create_ui()
        
        # Wire up callbacks
        self._setup_callbacks()
        
        # Start UI update loop
        self._process_ui_queue()
    
    def run(self) -> None:
        """Start the application main loop."""
        self.root.mainloop()


# Import ttk for UI components
from tkinter import ttk
