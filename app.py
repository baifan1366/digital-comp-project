"""
Study Planner Application - With Timer Functionality and Tab Navigation
"""
from datetime import datetime, timedelta
import os
import queue
import tkinter as tk
from tkinter import messagebox, ttk, Canvas

from study_planner.utils.validation import validate_numeric_input

# Color definitions - Enhanced modern palette
PRIMARY_BLUE = "#4A90E2"
PRIMARY_BLUE_DARK = "#357ABD"
SUCCESS = "#5CB85C"
SUCCESS_DARK = "#4CAF50"
WARNING = "#F0AD4E"
WARNING_DARK = "#EC971F"
INFO = "#5BC0DE"
INFO_DARK = "#46B8DA"
ERROR = "#D9534F"
ERROR_DARK = "#C9302C"
BG_LIGHT = "#F8F9FA"
BG_WHITE = "#FFFFFF"
BG_CARD = "#FFFFFF"
TEXT_PRIMARY = "#2C3E50"
TEXT_SECONDARY = "#7F8C8D"
BORDER_COLOR = "#D0D7DE"
BORDER_LIGHT = "#E8EDF2"
SHADOW_COLOR = "#00000010"

class StudyPlannerApp:
    def __init__(self):
        # Initialize storage
        app_dir = platformdirs.user_data_dir("StudyPlanner", "StudyPlannerApp")
        os.makedirs(app_dir, exist_ok=True)
        storage_path = os.path.join(app_dir, "data.json")
        self.storage = Storage(storage_path)
        
        # Initialize components
        self.plan_manager = PlanManager()
        self.history_manager = HistoryManager(self.storage)
        self.statistics_tracker = StatisticsTracker(self.storage)
        self.notifier = Notifier(popup_enabled=False, system_enabled=True, sound_enabled=True)
        
        # Currently selected plan
        self.selected_plan = None
        
        # UI update queue
        self.update_queue = queue.Queue()
        
        # Create window
        self.root = tk.Tk()
        self.root.title("Study Planner")
        self.root.geometry("950x720")  # Reduced height to fit screen
        self.root.configure(bg=BG_LIGHT)
        self.root.minsize(800, 600)  # Minimum size
        # Removed resizable(False, False) to allow user resizing
        
        # Build UI
        self._build_ui()
        
        # Initialize StudyPlanner
        self.study_planner = StudyPlanner(
            notifier=self.notifier,
            history=self.history_manager,
            stats=self.statistics_tracker
        )
        
        # Save original methods and wrap them to add UI updates
        self._original_on_timer_tick = self.study_planner._on_timer_tick
        self._original_on_phase_complete = self.study_planner._on_phase_complete
        
        def wrapped_on_timer_tick(remaining_seconds: int):
            # Call original method
            self._original_on_timer_tick(remaining_seconds)
            # Add UI update
            self._on_timer_tick(remaining_seconds)
        
        def wrapped_on_phase_complete():
            # Call original method
            self._original_on_phase_complete()
            # Add UI update
            self._on_phase_complete()
        
        # Replace methods
        self.study_planner._on_timer_tick = wrapped_on_timer_tick
        self.study_planner._on_phase_complete = wrapped_on_phase_complete
        
        # Start UI update loop
        self._process_updates()
        
        print("\n" + "="*60)
        print("Study Planner Started")
        print("="*60)
        print(f"Data storage: {storage_path}")
        print("\nFeatures:")
        print("1. Select preset plans or create custom plans")
        print("2. Click 'Start Study' to begin countdown")
        print("3. Real-time remaining time display")
        print("4. Automatic phase switching (study/break)")
        print("5. System notifications and sound alerts")
        print("="*60 + "\n")

    def _build_ui(self):
        """Build complete UI with tab navigation"""
        # Header bar with horizontal layout
        header = tk.Frame(self.root, bg=PRIMARY_BLUE, height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        # Title and subtitle in horizontal layout
        title_container = tk.Frame(header, bg=PRIMARY_BLUE)
        title_container.pack(side=tk.LEFT, padx=25, pady=12)
        
        tk.Label(
            title_container,
            text="📚 Study Planner",
            bg=PRIMARY_BLUE,
            fg="white",
            font=("Segoe UI", 16, "bold")
        ).pack(side=tk.LEFT)
        
        tk.Label(
            title_container,
            text="  •  Focus • Learn • Achieve",
            bg=PRIMARY_BLUE,
            fg="#E3F2FD",
            font=("Segoe UI", 11)
        ).pack(side=tk.LEFT, padx=(10, 0))
        
        # Tab navigation buttons in header
        nav_container = tk.Frame(header, bg=PRIMARY_BLUE)
        nav_container.pack(side=tk.RIGHT, padx=25, pady=12)
        
        self.nav_buttons = {}
        nav_items = [
            ("🏠 Home", "home"),
            ("📊 Analysis", "analysis"),
            ("📜 History", "history")
        ]
        
        for text, page_name in nav_items:
            btn = tk.Button(
                nav_container,
                text=text,
                bg=PRIMARY_BLUE_DARK if page_name == "home" else PRIMARY_BLUE,
                fg="white",
                font=("Segoe UI", 10, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                padx=15,
                pady=8,
                command=lambda p=page_name: self._switch_page(p)
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.nav_buttons[page_name] = btn
        
        # Main content area with tab pages
        main_container = tk.Frame(self.root, bg=BG_LIGHT)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Create pages container
        self.pages_container = tk.Frame(main_container, bg=BG_LIGHT)
        self.pages_container.pack(fill=tk.BOTH, expand=True)
        
        # Create all pages
        self.pages = {}
        self._create_home_page()
        self._create_analysis_page()
        self._create_history_page()
        
        # Show home page by default
        self.current_page = "home"
        self.pages["home"].pack(fill=tk.BOTH, expand=True)
    
    def _switch_page(self, page_name):
        """Switch between pages"""
        # Hide current page
        if self.current_page in self.pages:
            self.pages[self.current_page].pack_forget()
        
        # Show new page
        if page_name in self.pages:
            self.pages[page_name].pack(fill=tk.BOTH, expand=True)
            self.current_page = page_name
            
            # Update navigation button states
            for name, btn in self.nav_buttons.items():
                if name == page_name:
                    btn.config(bg=PRIMARY_BLUE_DARK)
                else:
                    btn.config(bg=PRIMARY_BLUE)
            
            # Refresh page data
            if page_name == "analysis":
                self._refresh_analysis_page()
            elif page_name == "history":
                self._refresh_history_page()
    
    def _create_home_page(self):
        """Create home page with study planner functionality"""
        # Create canvas and scrollbar for responsive design
        home_frame = tk.Frame(self.pages_container, bg=BG_LIGHT)
        self.pages["home"] = home_frame
        
        canvas = tk.Canvas(home_frame, bg=BG_LIGHT, highlightthickness=0)
        scrollbar = tk.Scrollbar(home_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_LIGHT)
        
        # Configure scrollable frame to expand with canvas width
        def _configure_scroll_region(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def _configure_canvas_width(event):
            # Make scrollable_frame width match canvas width
            canvas_width = event.width
            canvas.itemconfig(canvas_window, width=canvas_width)
        
        scrollable_frame.bind("<Configure>", _configure_scroll_region)
        canvas.bind("<Configure>", _configure_canvas_width)
        
        canvas_window = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Enable mouse wheel scrolling only when mouse is over canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)
        
        # Content frame (now inside scrollable_frame)
        content = tk.Frame(scrollable_frame, bg=BG_LIGHT)
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Store content reference for home page
        self.home_content = content
        
        # Timer display area with shadow effect
        timer_container = tk.Frame(content, bg=BG_LIGHT)
        timer_container.pack(fill=tk.X, pady=(0, 15))
        
        self.timer_frame = tk.Frame(
            timer_container, 
            bg=BG_CARD, 
            relief=tk.SOLID,
            borderwidth=2,
            highlightbackground=BORDER_COLOR,
            highlightcolor=BORDER_COLOR,
            highlightthickness=0
        )
        self.timer_frame.pack(fill=tk.X, padx=2, pady=2)
        
        # Timer display
        self.timer_label = tk.Label(
            self.timer_frame,
            text="00:00",
            bg=BG_CARD,
            fg=PRIMARY_BLUE,
            font=("Segoe UI", 48, "bold")
        )
        self.timer_label.pack(pady=(20, 8))
        
        # Phase label
        self.phase_label = tk.Label(
            self.timer_frame,
            text="Ready to Start",
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 12)
        )
        self.phase_label.pack(pady=(0, 20))
        
        # Preset plans area with modern card design
        preset_frame = tk.LabelFrame(
            content, 
            text="  Quick Start  ", 
            bg=BG_LIGHT, 
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            relief=tk.SOLID,
            borderwidth=2,
            highlightbackground=BORDER_COLOR,
            highlightthickness=0
        )
        preset_frame.pack(fill=tk.X, pady=(0, 15))
        
        preset_buttons_frame = tk.Frame(preset_frame, bg=BG_LIGHT)
        preset_buttons_frame.pack(fill=tk.X, padx=5, pady=10)
        
        presets = self.plan_manager.get_preset_plans()
        icons = {"Pomodoro": "🍅", "Deep Focus": "🎯", "Light Review": "📖"}
        
        for plan in presets:
            icon = icons.get(plan.name, "📝")
            # Build button text
            btn_text = f"{icon}\n{plan.name}\n{plan.study_minutes}min/{plan.break_minutes}min"
            if plan.cycles > 1:
                btn_text += f"\n×{plan.cycles} cycles"
            if plan.long_break_minutes > 0:
                btn_text += f"\n+{plan.long_break_minutes}min long break"
            
            # Create card-style button
            btn = tk.Button(
                preset_buttons_frame,
                text=btn_text,
                command=lambda p=plan: self._select_preset(p),
                bg=BG_CARD,
                fg=TEXT_PRIMARY,
                activebackground="#E3F2FD",
                activeforeground=PRIMARY_BLUE,
                font=("Segoe UI", 9),
                width=18,
                height=5,
                relief=tk.SOLID,
                borderwidth=2,
                highlightbackground=BORDER_LIGHT,
                highlightcolor=PRIMARY_BLUE,
                highlightthickness=0,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)
        
        # Custom plan area with modern card design
        custom_frame = tk.LabelFrame(
            content, 
            text="  Custom Plan  ", 
            bg=BG_LIGHT, 
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            relief=tk.SOLID,
            borderwidth=2,
            highlightbackground=BORDER_COLOR,
            highlightthickness=0
        )
        custom_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Card container with max width
        form_card = tk.Frame(
            custom_frame, 
            bg=BG_CARD,
            relief=tk.SOLID,
            borderwidth=2,
            highlightbackground=BORDER_LIGHT,
            highlightthickness=0
        )
        form_card.pack(fill=tk.X, padx=10, pady=10)
        
        # Inner container with max width constraint
        form_inner = tk.Frame(form_card, bg=BG_CARD)
        form_inner.pack(padx=15, pady=15)
        
        # Row 1: Plan Name (full width)
        row1 = tk.Frame(form_inner, bg=BG_CARD)
        row1.pack(fill=tk.X, pady=(0, 12))
        
        tk.Label(
            row1,
            text="Plan Name:",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.plan_name_entry = tk.Entry(
            row1,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=PRIMARY_BLUE,
            highlightthickness=1,
            width=50
        )
        self.plan_name_entry.insert(0, "Custom Plan")
        self.plan_name_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        # Row 2: Study Time and Break Time
        row2 = tk.Frame(form_inner, bg=BG_CARD)
        row2.pack(fill=tk.X, pady=(0, 12))
        
        # Study Time
        study_frame = tk.Frame(row2, bg=BG_CARD)
        study_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        tk.Label(
            study_frame,
            text="Study Time (min):",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.study_entry = tk.Entry(
            study_frame,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=PRIMARY_BLUE,
            highlightthickness=1,
            width=15
        )
        self.study_entry.pack(side=tk.LEFT, ipady=6)
        
        # Break Time
        break_frame = tk.Frame(row2, bg=BG_CARD)
        break_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            break_frame,
            text="Break Time (min):",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.break_entry = tk.Entry(
            break_frame,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=PRIMARY_BLUE,
            highlightthickness=1,
            width=15
        )
        self.break_entry.pack(side=tk.LEFT, ipady=6)
        
        # Row 3: Cycles and Long Break
        row3 = tk.Frame(form_inner, bg=BG_CARD)
        row3.pack(fill=tk.X, pady=(0, 12))
        
        # Cycles
        cycles_frame = tk.Frame(row3, bg=BG_CARD)
        cycles_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 20))
        
        tk.Label(
            cycles_frame,
            text="Cycles:",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.cycles_entry = tk.Entry(
            cycles_frame,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=PRIMARY_BLUE,
            highlightthickness=1,
            width=15
        )
        self.cycles_entry.insert(0, "1")
        self.cycles_entry.pack(side=tk.LEFT, ipady=6)
        
        # Long Break
        long_break_frame = tk.Frame(row3, bg=BG_CARD)
        long_break_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Label(
            long_break_frame,
            text="Long Break (min):",
            bg=BG_CARD,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 10),
            width=15,
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.long_break_entry = tk.Entry(
            long_break_frame,
            font=("Segoe UI", 10),
            relief=tk.SOLID,
            borderwidth=1,
            highlightbackground=BORDER_COLOR,
            highlightcolor=PRIMARY_BLUE,
            highlightthickness=1,
            width=15
        )
        self.long_break_entry.insert(0, "1")
        self.long_break_entry.pack(side=tk.LEFT, ipady=6)
        
        # Row 4: Help text and Create button
        row4 = tk.Frame(form_inner, bg=BG_CARD)
        row4.pack(fill=tk.X, pady=(0, 0))
        
        tk.Label(
            row4,
            text="(After all cycles complete)",
            bg=BG_CARD,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9)
        ).pack(side=tk.LEFT)
        
        tk.Button(
            row4,
            text="✓ Create Plan",
            command=self._create_custom,
            bg=PRIMARY_BLUE,
            fg="white",
            activebackground=PRIMARY_BLUE_DARK,
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=30,
            pady=10,
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        # Result display
        self.result_label = tk.Label(
            content,
            text="Please select a preset plan or create a custom plan",
            bg=BG_LIGHT,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 10)
        )
        self.result_label.pack(pady=12)
        
        # Control buttons with modern design
        controls_frame = tk.Frame(content, bg=BG_LIGHT)
        controls_frame.pack(fill=tk.X, pady=(5, 10))
        
        button_style = {
            "font": ("Segoe UI", 11, "bold"),
            "relief": tk.FLAT,
            "borderwidth": 0,
            "padx": 25,
            "pady": 15,
            "cursor": "hand2"
        }
        
        self.start_btn = tk.Button(
            controls_frame,
            text="▶ Start Study",
            command=self._on_start_session,
            bg=SUCCESS,
            fg="white",
            activebackground=SUCCESS_DARK,
            state=tk.DISABLED,
            **button_style
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.pause_btn = tk.Button(
            controls_frame,
            text="⏸ Pause",
            command=self._on_pause,
            bg=WARNING,
            fg="white",
            activebackground=WARNING_DARK,
            state=tk.DISABLED,
            **button_style
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.resume_btn = tk.Button(
            controls_frame,
            text="▶ Resume",
            command=self._on_resume,
            bg=INFO,
            fg="white",
            activebackground=INFO_DARK,
            state=tk.DISABLED,
            **button_style
        )
        self.resume_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
        self.stop_btn = tk.Button(
            controls_frame,
            text="⏹ Stop",
            command=self._on_stop,
            bg=ERROR,
            fg="white",
            activebackground=ERROR_DARK,
            state=tk.DISABLED,
            **button_style
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.X)
        
    def _create_analysis_page(self):
        """Create analysis page with statistics and charts"""
        analysis_frame = tk.Frame(self.pages_container, bg=BG_LIGHT)
        self.pages["analysis"] = analysis_frame
        
        # Create canvas for scrolling
        canvas = tk.Canvas(analysis_frame, bg=BG_LIGHT, highlightthickness=0)
        scrollbar = tk.Scrollbar(analysis_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=BG_LIGHT)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Enable mouse wheel scrolling for Analysis page
        def _on_mousewheel_analysis(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_mousewheel_analysis(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel_analysis)
        
        def _unbind_mousewheel_analysis(event):
            canvas.unbind_all("<MouseWheel>")
        
        canvas.bind("<Enter>", _bind_mousewheel_analysis)
        canvas.bind("<Leave>", _unbind_mousewheel_analysis)
        
        # Content
        content = tk.Frame(scrollable_frame, bg=BG_LIGHT)
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Page title
        tk.Label(
            content,
            text="📊 Study Analysis",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # Two column layout
        columns_frame = tk.Frame(content, bg=BG_LIGHT)
        columns_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left column - This Week/Month
        left_column = tk.Frame(columns_frame, bg=BG_LIGHT)
        left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Right column - All Time
        right_column = tk.Frame(columns_frame, bg=BG_LIGHT)
        right_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # === LEFT COLUMN: This Week/Month ===
        self._build_period_section(left_column)
        
        # === RIGHT COLUMN: All Time ===
        self._build_alltime_section(right_column)

    def _build_period_section(self, parent):
        """Build Last 7/30 Days section with toggle"""
        # Header with toggle button
        header_frame = tk.Frame(parent, bg=BG_LIGHT)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.period_label = tk.Label(
            header_frame,
            text="Last 7 Days Statistics",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 14, "bold")
        )
        self.period_label.pack(side=tk.LEFT)
        
        # Toggle button
        self.period_mode = "7days"  # "7days" or "30days"
        self.period_toggle_btn = tk.Button(
            header_frame,
            text="Switch to 30 Days",
            bg=PRIMARY_BLUE,
            fg="white",
            font=("Segoe UI", 9),
            relief=tk.FLAT,
            cursor="hand2",
            padx=10,
            pady=5,
            command=self._toggle_period
        )
        self.period_toggle_btn.pack(side=tk.RIGHT)
        
        # Statistics cards
        week_card = tk.LabelFrame(
            parent,
            text="  Statistics  ",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            relief=tk.SOLID,
            borderwidth=2
        )
        week_card.pack(fill=tk.X, pady=(0, 15))
        
        stats_container = tk.Frame(week_card, bg=BG_CARD)
        stats_container.pack(fill=tk.X, padx=15, pady=15)
        
        # Create 2x2 grid for statistics
        stats_items = [
            ("Total Study Time", "period_total_time", "0 minutes", SUCCESS),
            ("Study Sessions", "period_session_count", "0", INFO),
            ("Completed", "period_completed_count", "0", PRIMARY_BLUE),
            ("Interrupted", "period_interrupted_count", "0", WARNING)
        ]
        
        for i, (title, attr_name, default_value, color) in enumerate(stats_items):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(
                stats_container,
                bg=BG_WHITE,
                relief=tk.SOLID,
                borderwidth=1,
                highlightbackground=BORDER_LIGHT
            )
            stat_frame.grid(row=row, column=col, padx=(0, 10) if col == 0 else 0,
                           pady=(0, 10) if row == 0 else 0, sticky="ew")
            
            tk.Label(
                stat_frame,
                text=title,
                bg=BG_WHITE,
                fg=TEXT_SECONDARY,
                font=("Segoe UI", 9)
            ).pack(anchor=tk.W, padx=12, pady=(10, 3))
            
            value_label = tk.Label(
                stat_frame,
                text=default_value,
                bg=BG_WHITE,
                fg=color,
                font=("Segoe UI", 14, "bold")
            )
            value_label.pack(anchor=tk.W, padx=12, pady=(0, 10))
            
            setattr(self, attr_name, value_label)
        
        stats_container.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        
        # Chart with toggle
        chart_card = tk.LabelFrame(
            parent,
            text="  Visualization  ",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            relief=tk.SOLID,
            borderwidth=2
        )
        chart_card.pack(fill=tk.BOTH, expand=True)
        
        # Chart header with toggle button
        chart_header = tk.Frame(chart_card, bg=BG_CARD)
        chart_header.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        self.period_chart_mode = "bar"  # "bar" or "pie"
        self.period_chart_toggle_btn = tk.Button(
            chart_header,
            text="📊 → 🥧 Pie Chart",
            bg=INFO,
            fg="white",
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            cursor="hand2",
            padx=8,
            pady=4,
            command=self._toggle_period_chart
        )
        self.period_chart_toggle_btn.pack(side=tk.RIGHT)
        
        # Chart canvas
        chart_container = tk.Frame(chart_card, bg=BG_WHITE)
        chart_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.period_chart_canvas = Canvas(
            chart_container,
            bg=BG_WHITE,
            height=280,
            highlightthickness=0
        )
        self.period_chart_canvas.pack(fill=tk.BOTH, expand=True)

    def _build_alltime_section(self, parent):
        """Build All Time section"""
        # Header
        tk.Label(
            parent,
            text="All Time Statistics",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor=tk.W, pady=(0, 10))
        
        # Statistics cards
        alltime_card = tk.LabelFrame(
            parent,
            text="  Statistics  ",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            relief=tk.SOLID,
            borderwidth=2
        )
        alltime_card.pack(fill=tk.X, pady=(0, 15))
        
        stats_container = tk.Frame(alltime_card, bg=BG_CARD)
        stats_container.pack(fill=tk.X, padx=15, pady=15)
        
        # Create 2x2 grid for statistics
        stats_items = [
            ("Total Study Time", "alltime_total_time", "0 minutes", SUCCESS),
            ("Total Sessions", "alltime_session_count", "0", INFO),
            ("Total Completed", "alltime_completed_count", "0", PRIMARY_BLUE),
            ("Total Interrupted", "alltime_interrupted_count", "0", WARNING)
        ]
        
        for i, (title, attr_name, default_value, color) in enumerate(stats_items):
            row = i // 2
            col = i % 2
            
            stat_frame = tk.Frame(
                stats_container,
                bg=BG_WHITE,
                relief=tk.SOLID,
                borderwidth=1,
                highlightbackground=BORDER_LIGHT
            )
            stat_frame.grid(row=row, column=col, padx=(0, 10) if col == 0 else 0,
                           pady=(0, 10) if row == 0 else 0, sticky="ew")
            
            tk.Label(
                stat_frame,
                text=title,
                bg=BG_WHITE,
                fg=TEXT_SECONDARY,
                font=("Segoe UI", 9)
            ).pack(anchor=tk.W, padx=12, pady=(10, 3))
            
            value_label = tk.Label(
                stat_frame,
                text=default_value,
                bg=BG_WHITE,
                fg=color,
                font=("Segoe UI", 14, "bold")
            )
            value_label.pack(anchor=tk.W, padx=12, pady=(0, 10))
            
            setattr(self, attr_name, value_label)
        
        stats_container.columnconfigure(0, weight=1)
        stats_container.columnconfigure(1, weight=1)
        
        # Most used plan
        plan_frame = tk.Frame(
            stats_container,
            bg=BG_WHITE,
            relief=tk.SOLID,
            borderwidth=1
        )
        plan_frame.grid(row=2, column=0, columnspan=2, pady=(10, 0), sticky="ew")
        
        tk.Label(
            plan_frame,
            text="Most Used Plan",
            bg=BG_WHITE,
            fg=TEXT_SECONDARY,
            font=("Segoe UI", 9)
        ).pack(anchor=tk.W, padx=12, pady=(10, 3))
        
        self.most_used_plan_label = tk.Label(
            plan_frame,
            text="No data yet",
            bg=BG_WHITE,
            fg=PRIMARY_BLUE,
            font=("Segoe UI", 12, "bold")
        )
        self.most_used_plan_label.pack(anchor=tk.W, padx=12, pady=(0, 10))
        
        # Chart with toggle
        chart_card = tk.LabelFrame(
            parent,
            text="  Visualization  ",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            relief=tk.SOLID,
            borderwidth=2
        )
        chart_card.pack(fill=tk.BOTH, expand=True)
        
        # Chart header with toggle button
        chart_header = tk.Frame(chart_card, bg=BG_CARD)
        chart_header.pack(fill=tk.X, padx=15, pady=(10, 0))
        
        self.alltime_chart_mode = "bar"  # "bar" or "pie"
        self.alltime_chart_toggle_btn = tk.Button(
            chart_header,
            text="📊 → 🥧 Pie Chart",
            bg=INFO,
            fg="white",
            font=("Segoe UI", 8),
            relief=tk.FLAT,
            cursor="hand2",
            padx=8,
            pady=4,
            command=self._toggle_alltime_chart
        )
        self.alltime_chart_toggle_btn.pack(side=tk.RIGHT)
        
        # Chart canvas
        chart_container = tk.Frame(chart_card, bg=BG_WHITE)
        chart_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        self.alltime_chart_canvas = Canvas(
            chart_container,
            bg=BG_WHITE,
            height=280,
            highlightthickness=0
        )
        self.alltime_chart_canvas.pack(fill=tk.BOTH, expand=True)

    def _create_history_page(self):
        """Create history page with run history table"""
        history_frame = tk.Frame(self.pages_container, bg=BG_LIGHT)
        self.pages["history"] = history_frame
        
        # Content
        content = tk.Frame(history_frame, bg=BG_LIGHT)
        content.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)
        
        # Page title
        tk.Label(
            content,
            text="📜 Study History",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor=tk.W, pady=(0, 20))
        
        # History table card
        table_card = tk.LabelFrame(
            content,
            text="  Run History  ",
            bg=BG_LIGHT,
            fg=TEXT_PRIMARY,
            font=("Segoe UI", 11, "bold"),
            relief=tk.SOLID,
            borderwidth=2
        )
        table_card.pack(fill=tk.BOTH, expand=True)
        
        # Table container
        table_container = tk.Frame(table_card, bg=BG_WHITE)
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Create Treeview table
        columns = ("plan_name", "study_time", "break_time", "cycles", "timestamp")
        self.history_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            height=15
        )
        
        # Set column headings
        self.history_tree.heading("plan_name", text="Plan Name")
        self.history_tree.heading("study_time", text="Study Time")
        self.history_tree.heading("break_time", text="Break Time")
        self.history_tree.heading("cycles", text="Cycles")
        self.history_tree.heading("timestamp", text="Last Used")
        
        # Set column widths
        self.history_tree.column("plan_name", width=200)
        self.history_tree.column("study_time", width=100)
        self.history_tree.column("break_time", width=100)
        self.history_tree.column("cycles", width=80)
        self.history_tree.column("timestamp", width=180)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_container,
            orient=tk.VERTICAL,
            command=self.history_tree.yview
        )
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Run Again button
        btn_frame = tk.Frame(table_card, bg=BG_CARD)
        btn_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        tk.Button(
            btn_frame,
            text="▶ Run Again",
            command=self._run_again_selected,
            bg=SUCCESS,
            fg="white",
            activebackground=SUCCESS_DARK,
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            padx=25,
            pady=12,
            cursor="hand2"
        ).pack(side=tk.LEFT)

    def _select_preset(self, plan):
        """Select preset plan"""
        self.selected_plan = plan
        
        # Build description text
        desc = f"Selected: {plan.name} ({plan.study_minutes}min study / {plan.break_minutes}min break"
        if plan.cycles > 1:
            desc += f" × {plan.cycles} cycles"
        if plan.long_break_minutes > 0:
            desc += f" + {plan.long_break_minutes}min long break"
        desc += ")"
        
        self.result_label.config(text=desc, fg=SUCCESS)
        self.start_btn.config(state=tk.NORMAL)
        print(f"✓ Selected: {plan.name} - {plan.cycles} cycles" + (f" + {plan.long_break_minutes}min long break" if plan.long_break_minutes > 0 else ""))

    def _create_custom(self):
        """Create custom plan"""
        # Get plan name (use default if empty)
        plan_name = self.plan_name_entry.get().strip()
        if not plan_name:
            plan_name = "Custom Plan"
        
        study_str = self.study_entry.get().strip()
        break_str = self.break_entry.get().strip()
        cycles_str = self.cycles_entry.get().strip()
        long_break_str = self.long_break_entry.get().strip()
        
        study_min = validate_numeric_input(study_str)
        break_min = validate_numeric_input(break_str)
        cycles = validate_numeric_input(cycles_str) if cycles_str else 1
        
        # Handle long break - minimum value is 1
        if long_break_str:
            long_break_min = validate_numeric_input(long_break_str)
        else:
            long_break_min = 1
        
        if not study_min or not break_min:
            messagebox.showerror("Error", "Please enter valid study and break times")
            return
        
        if not cycles or cycles < 1:
            messagebox.showerror("Error", "Cycles must be at least 1")
            return
        
        if not long_break_min or long_break_min < 1:
            messagebox.showerror("Error", "Long break time must be at least 1 minute")
            return
        
        try:
            plan = self.plan_manager.create_custom_plan(
                name=plan_name,
                study_min=study_min,
                break_min=break_min,
                cycles=cycles,
                long_break_min=long_break_min
            )
            self.selected_plan = plan
            
            # Build description text
            desc = f"Created: {plan_name} - {study_min}min study / {break_min}min break × {cycles} cycles"
            if long_break_min > 0:
                desc += f" + {long_break_min}min long break"
            
            self.result_label.config(text=desc, fg=SUCCESS)
            self.start_btn.config(state=tk.NORMAL)
            print(f"✓ Created custom plan: {plan_name} - {study_min}/{break_min} × {cycles} cycles" + (f" + {long_break_min}min long break" if long_break_min > 0 else ""))
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _on_start_session(self):
        """Start study session"""
        if not self.selected_plan:
            messagebox.showwarning("Notice", "Please select a plan first")
            return
        
        try:
            # Start study session
            self.study_planner.start_session(self.selected_plan)
            
            # Update UI state
            self.start_btn.config(state=tk.DISABLED)
            self.pause_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.NORMAL)
            self.resume_btn.config(state=tk.DISABLED)
            
            # Refresh History page to show the new plan
            self._refresh_history_page()
            
            print(f"✓ Started study: {self.selected_plan.name}")
            
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
    
    def _on_pause(self):
        """Pause session"""
        try:
            self.study_planner.pause_session()
            self.pause_btn.config(state=tk.DISABLED)
            self.resume_btn.config(state=tk.NORMAL)
            self.phase_label.config(text="Paused")
            print("⏸ Paused")
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
    
    def _on_resume(self):
        """Resume session"""
        try:
            self.study_planner.resume_session()
            self.pause_btn.config(state=tk.NORMAL)
            self.resume_btn.config(state=tk.DISABLED)
            print("▶ Resumed")
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))
    
    def _on_stop(self):
        """Stop session"""
        self.study_planner.stop_session()
        
        # Reset UI
        self.timer_label.config(text="00:00")
        self.phase_label.config(text="Ready to Start")
        self.start_btn.config(state=tk.NORMAL if self.selected_plan else tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        self.resume_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Refresh Analysis and History pages with latest data
        self._refresh_analysis_page()
        self._refresh_history_page()
        
        print("⏹ Stopped")
    
    def _on_timer_tick(self, remaining_seconds: int):
        """Timer tick callback - called in background thread"""
        # Put UI update into queue
        self.update_queue.put(("tick", remaining_seconds))
    
    def _on_phase_complete(self):
        """Phase complete callback - called in background thread"""
        # Put phase complete event into queue
        self.update_queue.put(("phase_complete", None))
    
    def _process_updates(self):
        """Process UI update queue - called in main thread"""
        try:
            while True:
                event_type, data = self.update_queue.get_nowait()
                
                if event_type == "tick":
                    remaining_seconds = data
                    minutes = remaining_seconds // 60
                    seconds = remaining_seconds % 60
                    self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
                    
                    # Update phase display (including cycle info)
                    state = self.study_planner.get_current_state()
                    current_cycle = self.study_planner._current_cycle
                    total_cycles = self.study_planner._total_cycles
                    
                    if state.name == "STUDY":
                        if total_cycles > 1:
                            self.phase_label.config(text=f"Studying (Round {current_cycle}/{total_cycles})", fg=PRIMARY_BLUE)
                        else:
                            self.phase_label.config(text="Studying", fg=PRIMARY_BLUE)
                    elif state.name == "BREAK":
                        if total_cycles > 1:
                            self.phase_label.config(text=f"Break Time (Round {current_cycle}/{total_cycles})", fg=SUCCESS)
                        else:
                            self.phase_label.config(text="Break Time", fg=SUCCESS)
                    elif state.name == "LONG_BREAK":
                        self.phase_label.config(text="Long Break", fg=INFO)
                    elif state.name == "COMPLETED":
                        self.phase_label.config(text="Completed!", fg=SUCCESS)
                        self._on_session_complete()
                
                elif event_type == "phase_complete":
                    # Phase complete, check state
                    state = self.study_planner.get_current_state()
                    if state.name == "COMPLETED":
                        self._on_session_complete()
                
        except queue.Empty:
            pass
        
        # Check queue every 100ms
        self.root.after(100, self._process_updates)
    
    def _on_session_complete(self):
        """Session complete"""
        self.timer_label.config(text="Done!")
        self.phase_label.config(text="Congratulations! Study plan completed!", fg=SUCCESS)
        
        # Reset button states
        self.start_btn.config(state=tk.NORMAL if self.selected_plan else tk.DISABLED)
        self.pause_btn.config(state=tk.DISABLED)
        self.resume_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.DISABLED)
        
        # Refresh Analysis and History pages with latest data
        self._refresh_analysis_page()
        self._refresh_history_page()
        
        messagebox.showinfo("Completed", "Congratulations! You have completed your study plan!")
        print("✅ Study plan completed!")
    
    def _refresh_analysis_page(self):
        """Refresh analysis page with latest statistics"""
        # Calculate period data based on mode
        if self.period_mode == "7days":
            period_data = self._get_days_data(7)
        else:
            period_data = self._get_days_data(30)
        
        # Update period statistics
        self.period_total_time.config(text=format_duration(period_data["total_time"]))
        self.period_session_count.config(text=str(period_data["sessions"]))
        self.period_completed_count.config(text=str(period_data["completed"]))
        self.period_interrupted_count.config(text=str(period_data["interrupted"]))
        
        # Draw period chart
        title = f"Last {7 if self.period_mode == '7days' else 30} Days Overview"
        if self.period_chart_mode == "bar":
            self._draw_bar_chart(
                self.period_chart_canvas,
                period_data["total_time"],
                period_data["sessions"],
                period_data["completed"],
                period_data["interrupted"],
                title
            )
        else:
            self._draw_pie_chart(
                self.period_chart_canvas,
                period_data["total_time"],
                period_data["sessions"],
                period_data["completed"],
                period_data["interrupted"],
                title
            )
        
        # Calculate all-time data
        alltime_data = self._get_alltime_data()
        
        # Update all-time statistics
        self.alltime_total_time.config(text=format_duration(alltime_data["total_time"]))
        self.alltime_session_count.config(text=str(alltime_data["sessions"]))
        self.alltime_completed_count.config(text=str(alltime_data["completed"]))
        self.alltime_interrupted_count.config(text=str(alltime_data["interrupted"]))
        
        # Draw all-time chart
        if self.alltime_chart_mode == "bar":
            self._draw_bar_chart(
                self.alltime_chart_canvas,
                alltime_data["total_time"],
                alltime_data["sessions"],
                alltime_data["completed"],
                alltime_data["interrupted"],
                "All Time Overview"
            )
        else:
            self._draw_pie_chart(
                self.alltime_chart_canvas,
                alltime_data["total_time"],
                alltime_data["sessions"],
                alltime_data["completed"],
                alltime_data["interrupted"],
                "All Time Overview"
            )
        
        # Get most used plan from history
        recent_plans = self.history_manager.get_recent(100)
        if recent_plans:
            plan_counts = {}
            
            for plan in recent_plans:
                plan_name = plan.name
                if plan_name not in plan_counts:
                    plan_counts[plan_name] = 0
                plan_counts[plan_name] += 1
            
            # Find most used plan
            most_used = max(plan_counts.items(), key=lambda x: x[1])
            self.most_used_plan_label.config(text=f"{most_used[0]} ({most_used[1]} times)")
        else:
            self.most_used_plan_label.config(text="No data yet")
    
    def _get_days_data(self, days):
        """Get statistics for the last N days"""
        today = datetime.now().date()
        start_date = today - timedelta(days=days-1)  # Include today
        
        stats_data = self.statistics_tracker._stats
        
        # Calculate totals for the period
        total_time = 0
        completed = 0
        interrupted = 0
        
        # Iterate through all days in the period
        current_day = start_date
        while current_day <= today:
            day_key = current_day.isoformat()
            if day_key in stats_data.get("daily", {}):
                day_data = stats_data["daily"][day_key]
                total_time += day_data.get("total_study_minutes", 0)
                completed += day_data.get("completed_sessions", 0)
                interrupted += day_data.get("interrupted_sessions", 0)
            
            current_day += timedelta(days=1)
        
        # Total sessions = completed + interrupted
        sessions = completed + interrupted
        
        return {
            "total_time": total_time,
            "sessions": sessions,
            "completed": completed,
            "interrupted": interrupted
        }
    
    def _get_week_data(self):
        """Get this week's statistics (kept for compatibility)"""
        return self._get_days_data(7)
    
    def _get_month_data(self):
        """Get this month's statistics"""
        today = datetime.now().date()
        month_start = today.replace(day=1)
        
        stats_data = self.statistics_tracker._stats
        
        # Calculate month totals
        total_time = 0
        sessions = 0
        completed = 0
        interrupted = 0
        
        # Iterate through all days in the month
        current_day = month_start
        while current_day <= today:
            day_key = current_day.isoformat()
            if day_key in stats_data.get("daily", {}):
                day_data = stats_data["daily"][day_key]
                total_time += day_data.get("total_study_minutes", 0)
                sessions += day_data.get("completed_sessions", 0)
                interrupted += day_data.get("interrupted_sessions", 0)
            
            current_day += timedelta(days=1)
        
        # Count completed pomodoros for the month
        for week_key, week_data in stats_data.get("weekly", {}).items():
            week_date = datetime.fromisoformat(week_key).date()
            if month_start <= week_date <= today:
                completed += week_data.get("completed_pomodoros", 0)
        
        return {
            "total_time": total_time,
            "sessions": sessions,
            "completed": completed,
            "interrupted": interrupted
        }
    
    def _get_alltime_data(self):
        """Get all-time statistics"""
        stats_data = self.statistics_tracker._stats
        
        # Calculate all-time totals
        total_time = 0
        completed = 0
        interrupted = 0
        
        for day_data in stats_data.get("daily", {}).values():
            total_time += day_data.get("total_study_minutes", 0)
            completed += day_data.get("completed_sessions", 0)
            interrupted += day_data.get("interrupted_sessions", 0)
        
        # Total sessions = completed + interrupted
        sessions = completed + interrupted
        
        return {
            "total_time": total_time,
            "sessions": sessions,
            "completed": completed,
            "interrupted": interrupted
        }
    
    def run(self):
        """run app"""
        self.root.mainloop()
        
if __name__ == "__main__":
    app = StudyPlannerApp()
    app.run()
