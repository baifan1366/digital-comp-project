"""
Study Planner Application - With Timer Functionality and Tab Navigation
"""
import tkinter as tk
from tkinter import messagebox, ttk, Canvas

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
        
        
    def run(self):
        """run app"""
        self.root.mainloop()
        
if __name__ == "__main__":
    app = StudyPlannerApp()
    app.run()