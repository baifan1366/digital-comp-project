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
    
    def _create_ui(self) -> None:
        """Create and layout UI components."""
        # Create main container
        container = ttk.Frame(self.root)
        container.pack(fill=tk.BOTH, expand=True)
        
        # Create timer display at top
        timer_frame = ttk.Frame(container)
        timer_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)
        self.timer_display = TimerDisplay(timer_frame)
        
        # Create navigation view below timer
        main_frame = ttk.Frame(container)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.main_window = NavigationView(
            main_frame,
            self.plan_manager,
            self.history_manager,
            self.statistics_tracker
        )
    
    def _setup_callbacks(self) -> None:
        """Wire up callbacks between UI and core logic."""
        # Connect main window callbacks
        self.main_window.set_start_callback(self._on_start_session)
        self.main_window.set_pause_callback(self._on_pause_session)
        self.main_window.set_resume_callback(self._on_resume_session)
        self.main_window.set_stop_callback(self._on_stop_session)
        
        # Override notifier methods to use UI popups
        self._setup_notifier_callbacks()
    
    def _setup_notifier_callbacks(self) -> None:
        """Setup notifier to use UI popup dialogs."""
        # Store original methods
        original_send_popup = self.notifier._send_popup
        
        # Override popup method to use UI dialogs
        def send_popup_ui(message: str) -> None:
            # Queue UI update for thread safety
            if "Study time" in message or "study" in message.lower():
                self.ui_queue.put(("notification", "study_start"))
            elif "Break time" in message or "break" in message.lower():
                if "Long" in message:
                    self.ui_queue.put(("notification", "long_break_start"))
                else:
                    self.ui_queue.put(("notification", "break_start"))
            elif "complete" in message.lower():
                self.ui_queue.put(("notification", "session_complete"))
        
        self.notifier._send_popup = send_popup_ui
    
    def _on_start_session(self, plan: StudyPlan) -> None:
        """
        Handle start session request from UI.
        
        Args:
            plan: StudyPlan to start
        """
        try:
            self.planner.start_session(plan)
            
            # Update UI state
            self.main_window.set_session_active(True)
            
            # Setup timer callbacks for UI updates
            self._setup_timer_callbacks()
            
            # Initial UI update
            self._update_timer_display()
            
        except RuntimeError as e:
            self.main_window._show_error(str(e))
    
    def _on_pause_session(self) -> None:
        """Handle pause session request from UI."""
        try:
            self.planner.pause_session()
            self.main_window.set_session_paused(True)
            self._update_timer_display()
            
        except RuntimeError as e:
            self.main_window._show_error(str(e))
    
    def _on_resume_session(self) -> None:
        """Handle resume session request from UI."""
        try:
            self.planner.resume_session()
            self.main_window.set_session_paused(False)
            self._update_timer_display()
            
        except RuntimeError as e:
            self.main_window._show_error(str(e))
    
    def _on_stop_session(self) -> None:
        """Handle stop session request from UI."""
        self.planner.stop_session()
        self.main_window.set_session_active(False)
        self._update_timer_display()
    
    def _setup_timer_callbacks(self) -> None:
        """
        Setup timer callbacks to queue UI updates.
        
        This ensures thread-safe communication from timer thread to UI thread.
        """
        # The timer callbacks are already set up in StudyPlanner
        # We just need to poll for updates
        pass
    
    def _update_timer_display(self) -> None:
        """Update timer display with current state."""
        state = self.planner.get_current_state()
        plan = self.planner.get_current_plan()
        
        # Update state
        self.timer_display.update_state(state)
        
        # Update time
        if hasattr(self.planner, '_current_timer') and self.planner._current_timer:
            remaining = self.planner._current_timer.get_remaining_seconds()
            self.timer_display.update_time(remaining)
        else:
            self.timer_display.update_time(0)
        
        # Update cycle info
        if plan and hasattr(self.planner, '_current_cycle'):
            self.timer_display.update_cycle(
                self.planner._current_cycle,
                self.planner._total_cycles
            )
        else:
            self.timer_display.update_cycle(0, 0)
        
        # Schedule next update if session is active
        if state not in (SessionState.IDLE, SessionState.COMPLETED):
            self.root.after(1000, self._update_timer_display)
    
    def _process_ui_queue(self) -> None:
        """
        Process queued UI updates from timer thread.
        
        This method runs in the UI thread and processes updates
        queued by timer callbacks running in background threads.
        """
        try:
            while not self.ui_queue.empty():
                update_type, data = self.ui_queue.get_nowait()
                
                if update_type == "notification":
                    self._show_notification(data)
                elif update_type == "timer_update":
                    self._update_timer_display()
        
        except Exception as e:
            print(f"Error processing UI queue: {e}")
        
        # Schedule next queue check
        self.root.after(100, self._process_ui_queue)
    
    def _show_notification(self, notification_type: str) -> None:
        """
        Show notification popup.
        
        Args:
            notification_type: Type of notification to show
        """
        if notification_type == "study_start":
            NotificationPopup.show_study_start(self.root)
        elif notification_type == "break_start":
            NotificationPopup.show_break_start(self.root)
        elif notification_type == "long_break_start":
            NotificationPopup.show_long_break_start(self.root)
        elif notification_type == "session_complete":
            NotificationPopup.show_session_complete(self.root)
    
    def run(self) -> None:
        """Start the application main loop."""
        self.root.mainloop()


# Import ttk for UI components
from tkinter import ttk
