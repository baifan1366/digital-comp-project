"""
Study Planner Application - With Timer Functionality and Tab Navigation
"""
import tkinter as tk
from tkinter import messagebox, ttk, Canvas

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

    def run(self):
        """run app"""
        self.root.mainloop()

if __name__ == "__main__":
    app = StudyPlannerApp()
    app.run()