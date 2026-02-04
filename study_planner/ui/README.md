# Study Planner UI Layer

This directory contains the Tkinter-based user interface components for the Study Planner application.

## Components

### MainWindow (`main_view.py`)
The primary application window providing:
- Preset plan selection buttons (Pomodoro, Deep Focus, Light Review)
- Custom plan configuration form with validation
- History display showing 5 most recent configurations
- Session control buttons (Start, Pause, Resume, Stop)
- Error message display for validation feedback

**Key Features:**
- Input validation for all time parameters (1-180 minutes)
- Cycle count validation (≥1)
- Configuration modification prevention during active sessions
- Clickable history entries for quick plan reuse

### TimerDisplay (`timer_view.py`)
Visual countdown timer component displaying:
- MM:SS format countdown
- Current state indicator (Study, Break, Long Break, etc.)
- Cycle progress (e.g., "Cycle 2 of 4")
- Color-coded state labels

**Update Methods:**
- `update_time(remaining_seconds)` - Updates countdown display
- `update_state(state)` - Updates state label and color
- `update_cycle(current, total)` - Updates cycle progress

### NotificationPopup (`dialogs.py`)
Popup notification dialogs for phase transitions:
- Study start notification
- Break start notification
- Long break start notification
- Session complete notification

### NotificationSettingsDialog (`dialogs.py`)
Modal dialog for configuring notification preferences:
- Enable/disable popup notifications
- Enable/disable system notifications
- Enable/disable sound alerts

### AppController (`app_controller.py`)
Integration controller connecting UI with core logic:
- Thread-safe communication between timer callbacks and UI updates
- Session state synchronization
- Configuration modification prevention
- Notification delivery through UI popups

**Key Responsibilities:**
- Manages UI update queue for thread safety
- Wires up callbacks between UI and StudyPlanner
- Handles timer display updates every second
- Processes notification requests from background threads

## Usage

### Basic Usage with AppController

```python
import tkinter as tk
from study_planner.ui import AppController
from study_planner.core.planner import StudyPlanner
from study_planner.core.plans import PlanManager
from study_planner.core.notifier import Notifier
from study_planner.data.history import HistoryManager
from study_planner.data.statistics import StatisticsTracker
from study_planner.data.storage import Storage

# Create root window
root = tk.Tk()

# Initialize components
storage = Storage("data.json")
plan_manager = PlanManager(storage)
history_manager = HistoryManager(storage)
stats_tracker = StatisticsTracker(storage)
notifier = Notifier()
planner = StudyPlanner(notifier, history_manager, stats_tracker)

# Create controller (handles all integration)
app = AppController(root, planner, plan_manager, history_manager, notifier)

# Run application
app.run()
```

### Manual Component Usage

```python
import tkinter as tk
from study_planner.ui import MainWindow, TimerDisplay
from study_planner.core.plans import PlanManager
from study_planner.data.history import HistoryManager
from study_planner.data.storage import Storage

root = tk.Tk()
storage = Storage("data.json")

# Create managers
plan_manager = PlanManager(storage)
history_manager = HistoryManager(storage)

# Create UI components
main_window = MainWindow(root, plan_manager, history_manager)
timer_display = TimerDisplay(root)

# Set up callbacks
def on_start(plan):
    print(f"Starting: {plan.name}")
    main_window.set_session_active(True)

main_window.set_start_callback(on_start)

root.mainloop()
```

## Thread Safety

The UI layer is designed to work with the multi-threaded timer engine:

1. **Timer callbacks** run in background threads
2. **UI updates** are queued via `Queue` for thread safety
3. **AppController** processes the queue in the UI thread
4. **All Tkinter operations** happen in the main UI thread

## Requirements Validation

The UI layer implements the following requirements:

- **1.1, 1.2, 1.3**: Preset plan buttons for Pomodoro, Deep Focus, Light Review
- **1.4**: Preset plan loading on selection
- **2.1, 2.2**: Time input validation (1-180 minutes)
- **2.3, 2.4**: Invalid input rejection with error messages
- **3.2, 3.3**: History display with clickable entries
- **4.1, 4.3**: MM:SS countdown timer display
- **5.6**: Configuration modification prevention during active session
- **6.1, 6.2, 6.3**: Phase transition notifications
- **6.4, 6.7**: Notification channel configuration
- **9.3, 9.4, 9.5**: Input validation and error messages
- **10.1, 10.2, 10.3**: Session control integration

## Testing

See `demo_ui.py` for a standalone UI demo without full integration.
See `app_example.py` for a complete application example with full integration.
