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

    def _build_ui(self) -> None:
        """Build the complete user interface."""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Preset Plans Section
        self._build_preset_section(main_frame)
        
        # Custom Plan Section
        self._build_custom_section(main_frame)
        
        # History Section
        self._build_history_section(main_frame)
        
        # Statistics Section (if tracker is available)
        if self.statistics_tracker:
            self._build_statistics_section(main_frame)
        
        # Control Buttons Section
        self._build_controls_section(main_frame)
        
        # Error message label
        self.error_label = ttk.Label(
            main_frame,
            text="",
            foreground="red",
            wraplength=550
        )
        self.error_label.grid(row=5, column=0, pady=5, sticky=tk.W)
    
    def _build_preset_section(self, parent: ttk.Frame) -> None:
        """Build preset plan selection section."""
        preset_frame = ttk.LabelFrame(parent, text="Preset Plans", padding="10")
        preset_frame.grid(row=0, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Get preset plans
        presets = self.plan_manager.get_preset_plans()
        
        # Create button for each preset
        for i, plan in enumerate(presets):
            btn_text = f"{plan.name}\n({plan.study_minutes}m study / {plan.break_minutes}m break"
            if plan.cycles > 1:
                btn_text += f" / {plan.cycles} cycles"
            if plan.long_break_minutes > 0:
                btn_text += f" / {plan.long_break_minutes}m long break"
            btn_text += ")"
            
            btn = ttk.Button(
                preset_frame,
                text=btn_text,
                command=lambda p=plan: self._select_preset(p)
            )
            btn.grid(row=0, column=i, padx=5, sticky=(tk.W, tk.E))
            preset_frame.columnconfigure(i, weight=1)
    
    def _build_custom_section(self, parent: ttk.Frame) -> None:
        """Build custom plan configuration section."""
        custom_frame = ttk.LabelFrame(parent, text="Custom Plan", padding="10")
        custom_frame.grid(row=1, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Plan name
        ttk.Label(custom_frame, text="Plan Name:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.name_entry = ttk.Entry(custom_frame, width=30)
        self.name_entry.grid(row=0, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=2)
        self.name_entry.insert(0, "Custom Plan")
        
        # Study time
        ttk.Label(custom_frame, text="Study Time (min):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.study_entry = ttk.Entry(custom_frame, width=15)
        self.study_entry.grid(row=1, column=1, sticky=tk.W, pady=2)
        ttk.Label(custom_frame, text="(1-180)").grid(row=1, column=2, sticky=tk.W, pady=2)
        
        # Break time
        ttk.Label(custom_frame, text="Break Time (min):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.break_entry = ttk.Entry(custom_frame, width=15)
        self.break_entry.grid(row=2, column=1, sticky=tk.W, pady=2)
        ttk.Label(custom_frame, text="(1-180)").grid(row=2, column=2, sticky=tk.W, pady=2)
        
        # Cycles
        ttk.Label(custom_frame, text="Cycles:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.cycles_entry = ttk.Entry(custom_frame, width=15)
        self.cycles_entry.grid(row=3, column=1, sticky=tk.W, pady=2)
        self.cycles_entry.insert(0, "1")
        ttk.Label(custom_frame, text="(≥1)").grid(row=3, column=2, sticky=tk.W, pady=2)
        
        # Long break
        ttk.Label(custom_frame, text="Long Break (min):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.long_break_entry = ttk.Entry(custom_frame, width=15)
        self.long_break_entry.grid(row=4, column=1, sticky=tk.W, pady=2)
        self.long_break_entry.insert(0, "0")
        ttk.Label(custom_frame, text="(0-180, optional)").grid(row=4, column=2, sticky=tk.W, pady=2)
        
        # Create custom plan button
        self.create_btn = ttk.Button(
            custom_frame,
            text="Create Custom Plan",
            command=self._create_custom_plan
        )
        self.create_btn.grid(row=5, column=0, columnspan=3, pady=10)
        
        custom_frame.columnconfigure(1, weight=1)
    
    def _build_history_section(self, parent: ttk.Frame) -> None:
        """Build history display section."""
        history_frame = ttk.LabelFrame(parent, text="Recent Configurations", padding="10")
        history_frame.grid(row=2, column=0, pady=10, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollable listbox for history
        list_frame = ttk.Frame(history_frame)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        self.history_listbox = tk.Listbox(
            list_frame,
            height=5,
            yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.history_listbox.yview)
        
        self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Bind selection event
        self.history_listbox.bind('<<ListboxSelect>>', self._on_history_select)
        
        # Load history button
        load_btn = ttk.Button(
            history_frame,
            text="Load Selected",
            command=self._load_from_history
        )
        load_btn.grid(row=1, column=0, pady=5)
        
        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)
        
        # Populate history
        self._refresh_history()
    
    def _build_statistics_section(self, parent: ttk.Frame) -> None:
        """Build statistics display section."""
        stats_frame = ttk.LabelFrame(parent, text="Study Statistics", padding="10")
        stats_frame.grid(row=3, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Create a grid layout for statistics
        # Today's study time
        ttk.Label(stats_frame, text="Today's Study Time:", font=("TkDefaultFont", 9, "bold")).grid(
            row=0, column=0, sticky=tk.W, pady=2, padx=(0, 10)
        )
        self.today_time_label = ttk.Label(stats_frame, text="0 minutes")
        self.today_time_label.grid(row=0, column=1, sticky=tk.W, pady=2)
        
        # Weekly study time
        ttk.Label(stats_frame, text="This Week's Study Time:", font=("TkDefaultFont", 9, "bold")).grid(
            row=1, column=0, sticky=tk.W, pady=2, padx=(0, 10)
        )
        self.week_time_label = ttk.Label(stats_frame, text="0 minutes")
        self.week_time_label.grid(row=1, column=1, sticky=tk.W, pady=2)
        
        # Completed pomodoros
        ttk.Label(stats_frame, text="Completed Sessions:", font=("TkDefaultFont", 9, "bold")).grid(
            row=2, column=0, sticky=tk.W, pady=2, padx=(0, 10)
        )
        self.completed_label = ttk.Label(stats_frame, text="0")
        self.completed_label.grid(row=2, column=1, sticky=tk.W, pady=2)
        
        # Interrupted sessions
        ttk.Label(stats_frame, text="Interrupted Sessions:", font=("TkDefaultFont", 9, "bold")).grid(
            row=3, column=0, sticky=tk.W, pady=2, padx=(0, 10)
        )
        self.interrupted_label = ttk.Label(stats_frame, text="0")
        self.interrupted_label.grid(row=3, column=1, sticky=tk.W, pady=2)
        
        stats_frame.columnconfigure(1, weight=1)
        
        # Initial statistics update
        self._update_statistics_display()
    
    def _build_controls_section(self, parent: ttk.Frame) -> None:
        """Build session control buttons section."""
        controls_frame = ttk.Frame(parent, padding="10")
        controls_frame.grid(row=4, column=0, pady=10, sticky=(tk.W, tk.E))
        
        # Start button
        self.start_btn = ttk.Button(
            controls_frame,
            text="Start Session",
            command=self._on_start_clicked,
            state=tk.DISABLED
        )
        self.start_btn.grid(row=0, column=0, padx=5, sticky=(tk.W, tk.E))
        
        # Pause button
        self.pause_btn = ttk.Button(
            controls_frame,
            text="Pause",
            command=self._on_pause_clicked,
            state=tk.DISABLED
        )
        self.pause_btn.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))
        
        # Resume button
        self.resume_btn = ttk.Button(
            controls_frame,
            text="Resume",
            command=self._on_resume_clicked,
            state=tk.DISABLED
        )
        self.resume_btn.grid(row=0, column=2, padx=5, sticky=(tk.W, tk.E))
        
        # Stop button
        self.stop_btn = ttk.Button(
            controls_frame,
            text="Stop",
            command=self._on_stop_clicked,
            state=tk.DISABLED
        )
        self.stop_btn.grid(row=0, column=3, padx=5, sticky=(tk.W, tk.E))
        
        for i in range(4):
            controls_frame.columnconfigure(i, weight=1)

    def _select_preset(self, plan: StudyPlan) -> None:
        """
        Handle preset plan selection.
        
        Args:
            plan: Selected preset StudyPlan
        """
        if self._session_active and not self._can_modify():
            self._show_error("Cannot change plan during active session")
            return
        
        self._selected_plan = plan
        self._clear_error()
        self.start_btn.config(state=tk.NORMAL)
        
        # Update custom form to show preset values
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, plan.name)
        self.study_entry.delete(0, tk.END)
        self.study_entry.insert(0, str(plan.study_minutes))
        self.break_entry.delete(0, tk.END)
        self.break_entry.insert(0, str(plan.break_minutes))
        self.cycles_entry.delete(0, tk.END)
        self.cycles_entry.insert(0, str(plan.cycles))
        self.long_break_entry.delete(0, tk.END)
        self.long_break_entry.insert(0, str(plan.long_break_minutes))
    
    def _create_custom_plan(self) -> None:
        """Handle custom plan creation with validation."""
        if self._session_active and not self._can_modify():
            self._show_error("Cannot change plan during active session")
            return
        
        # Get and validate inputs
        name = self.name_entry.get().strip()
        if not name:
            self._show_error("Please enter a plan name")
            return
        
        # Validate study time
        study_str = self.study_entry.get().strip()
        study_min = validate_numeric_input(study_str)
        if study_min is None:
            self._show_error("Please enter a valid number for study time")
            return
        
        # Validate break time
        break_str = self.break_entry.get().strip()
        break_min = validate_numeric_input(break_str)
        if break_min is None:
            self._show_error("Please enter a valid number for break time")
            return
        
        # Validate cycles
        cycles_str = self.cycles_entry.get().strip()
        cycles = validate_numeric_input(cycles_str)
        if cycles is None:
            self._show_error("Please enter a valid number for cycles")
            return
        
        # Validate long break (0 is allowed)
        long_break_str = self.long_break_entry.get().strip()
        try:
            long_break_min = int(long_break_str)
            if long_break_min < 0:
                self._show_error("Long break time cannot be negative")
                return
        except ValueError:
            self._show_error("Please enter a valid number for long break time")
            return
        
        # Create plan with validation
        try:
            plan = self.plan_manager.create_custom_plan(
                name=name,
                study_min=study_min,
                break_min=break_min,
                cycles=cycles,
                long_break_min=long_break_min
            )
            
            self._selected_plan = plan
            self._clear_error()
            self.start_btn.config(state=tk.NORMAL)
            
        except ValueError as e:
            self._show_error(str(e))
    
    def _refresh_history(self) -> None:
        """Refresh the history listbox with recent configurations."""
        self.history_listbox.delete(0, tk.END)
        
        recent_plans = self.history_manager.get_recent(5)
        for plan in recent_plans:
            display_text = f"{plan.name}: {plan.study_minutes}m/{plan.break_minutes}m"
            if plan.cycles > 1:
                display_text += f", {plan.cycles} cycles"
            if plan.long_break_minutes > 0:
                display_text += f", {plan.long_break_minutes}m long break"
            
            self.history_listbox.insert(tk.END, display_text)
    
    def _on_history_select(self, event) -> None:
        """Handle history listbox selection event."""
        # Just highlight, actual load happens on button click
        pass
    
    def _load_from_history(self) -> None:
        """Load selected configuration from history."""
        if self._session_active and not self._can_modify():
            self._show_error("Cannot change plan during active session")
            return
        
        selection = self.history_listbox.curselection()
        if not selection:
            self._show_error("Please select a configuration from history")
            return
        
        index = selection[0]
        recent_plans = self.history_manager.get_recent(5)
        
        if index < len(recent_plans):
            plan = recent_plans[index]
            self._select_preset(plan)  # Reuse preset selection logic
    
    def _on_start_clicked(self) -> None:
        """Handle start button click."""
        if not self._selected_plan:
            self._show_error("Please select or create a plan first")
            return
        
        if self._on_start_callback:
            self._on_start_callback(self._selected_plan)
    
    def _on_pause_clicked(self) -> None:
        """Handle pause button click."""
        if self._on_pause_callback:
            self._on_pause_callback()
    
    def _on_resume_clicked(self) -> None:
        """Handle resume button click."""
        if self._on_resume_callback:
            self._on_resume_callback()
    
    def _on_stop_clicked(self) -> None:
        """Handle stop button click."""
        if self._on_stop_callback:
            self._on_stop_callback()
    
    def _show_error(self, message: str) -> None:
        """
        Display error message.
        
        Args:
            message: Error message to display
        """
        self.error_label.config(text=message)
    
    def _clear_error(self) -> None:
        """Clear error message display."""
        self.error_label.config(text="")
    
    def _can_modify(self) -> bool:
        """
        Check if plan modification is allowed.
        
        Returns:
            True if modification is allowed, False otherwise
        """
        # This will be connected to StudyPlanner.can_modify_plan()
        return not self._session_active
    
    def _update_statistics_display(self) -> None:
        """
        Update the statistics display with current values.
        
        Fetches latest statistics from the tracker and updates UI labels.
        """
        if not self.statistics_tracker:
            return
        
        # Get statistics
        today_minutes = self.statistics_tracker.get_today_study_time()
        week_minutes = self.statistics_tracker.get_week_study_time()
        completed_count = self.statistics_tracker.get_completed_pomodoros()
        interrupted_count = self.statistics_tracker.get_interrupted_count()
        
        # Update labels
        self.today_time_label.config(text=format_duration(today_minutes))
        self.week_time_label.config(text=format_duration(week_minutes))
        self.completed_label.config(text=str(completed_count))
        self.interrupted_label.config(text=str(interrupted_count))
    