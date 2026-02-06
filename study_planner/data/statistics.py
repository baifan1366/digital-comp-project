"""
Statistics tracking for study sessions.

Records and aggregates study session data including completed sessions,
interrupted sessions, and time tracking with daily and weekly views.
"""

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from study_planner.core.plans import StudyPlan
    from study_planner.data.storage import Storage


class StatisticsTracker:
    """
    Records and aggregates study session data.
    
    Tracks completed and interrupted sessions, accumulates study time
    by day and week, and provides statistics queries. All data is
    persisted to storage immediately on updates.
    """
    
    def __init__(self, storage: 'Storage'):
        """
        Initialize StatisticsTracker with storage backend.
        
        Args:
            storage: Storage instance for persisting statistics data
        """
        self.storage = storage
        self._stats = {
            "daily": {},
            "weekly": {},
            "completed_pomodoros": 0,
            "interrupted_count": 0
        }
        
        # Load existing statistics from storage
        self._load_stats()
    
    def record_completed_session(self, plan: 'StudyPlan', actual_study_minutes: int) -> None:
        """
        Record a successfully completed study session.
        
        Updates daily and weekly study time, increments completed session count,
        and persists data immediately.
        
        Args:
            plan: The StudyPlan that was completed
            actual_study_minutes: Actual study time completed in minutes
        """
        today = datetime.now().date().isoformat()
        week_start = self._get_week_start().isoformat()
        
        # Update daily stats
        if today not in self._stats["daily"]:
            self._stats["daily"][today] = {
                "total_study_minutes": 0,
                "completed_sessions": 0,
                "interrupted_sessions": 0
            }
        
        self._stats["daily"][today]["total_study_minutes"] += actual_study_minutes
        self._stats["daily"][today]["completed_sessions"] += 1
        
        # Update weekly stats
        if week_start not in self._stats["weekly"]:
            self._stats["weekly"][week_start] = {
                "total_study_minutes": 0,
                "completed_pomodoros": 0
            }
        
        self._stats["weekly"][week_start]["total_study_minutes"] += actual_study_minutes
        
        # Increment completed pomodoros count
        self._stats["completed_pomodoros"] += 1
        self._stats["weekly"][week_start]["completed_pomodoros"] += 1
        
        # Persist to storage
        self._save_stats()
    
    def record_interrupted_session(self, plan: 'StudyPlan', partial_study_minutes: int) -> None:
        """
        Record an interrupted or stopped study session.
        
        Updates interrupted session count but does not count partial time
        toward study time totals. Persists data immediately.
        
        Args:
            plan: The StudyPlan that was interrupted
            partial_study_minutes: Partial study time before interruption (not counted)
        """
        today = datetime.now().date().isoformat()
        
        # Update daily stats
        if today not in self._stats["daily"]:
            self._stats["daily"][today] = {
                "total_study_minutes": 0,
                "completed_sessions": 0,
                "interrupted_sessions": 0
            }
        
        self._stats["daily"][today]["interrupted_sessions"] += 1
        
        # Increment global interrupted count
        self._stats["interrupted_count"] += 1
        
        # Persist to storage
        self._save_stats()
    
    def get_today_study_time(self) -> int:
        """
        Get total study time completed today.
        
        Returns:
            Total study minutes completed today
        """
        today = datetime.now().date().isoformat()
        
        if today in self._stats["daily"]:
            return self._stats["daily"][today]["total_study_minutes"]
        
        return 0
    
    def get_week_study_time(self) -> int:
        """
        Get total study time for the current week.
        
        Returns:
            Total study minutes completed this week
        """
        week_start = self._get_week_start().isoformat()
        
        if week_start in self._stats["weekly"]:
            return self._stats["weekly"][week_start]["total_study_minutes"]
        
        return 0
    
    def get_completed_pomodoros(self) -> int:
        """
        Get count of completed pomodoro sessions.
        
        Returns:
            Total number of completed study sessions
        """
        return self._stats["completed_pomodoros"]
    
    def get_interrupted_count(self) -> int:
        """
        Get count of interrupted sessions.
        
        Returns:
            Total number of interrupted or stopped sessions
        """
        return self._stats["interrupted_count"]
    
    def reset_daily_stats(self) -> None:
        """
        Reset daily statistics.
        
        Called at midnight to start fresh daily tracking.
        Preserves historical data but resets current day counters.
        """
        today = datetime.now().date().isoformat()
        
        # Reset today's stats
        if today in self._stats["daily"]:
            self._stats["daily"][today] = {
                "total_study_minutes": 0,
                "completed_sessions": 0,
                "interrupted_sessions": 0
            }
        
        # Persist to storage
        self._save_stats()
    
    def _get_week_start(self) -> datetime.date:
        """
        Get the start date of the current week (Monday).
        
        Returns:
            Date object representing the Monday of the current week
        """
        today = datetime.now().date()
        # Calculate days since Monday (0 = Monday, 6 = Sunday)
        days_since_monday = today.weekday()
        week_start = today - timedelta(days=days_since_monday)
        return week_start
    
    def _load_stats(self) -> None:
        """
        Load statistics from storage.
        
        Internal method called during initialization.
        Handles corrupted or missing data gracefully.
        """
        try:
            data = self.storage.load()
            stats_data = data.get("statistics", {})
            
            # Validate and load statistics data
            if isinstance(stats_data, dict):
                self._stats = {
                    "daily": stats_data.get("daily", {}),
                    "weekly": stats_data.get("weekly", {}),
                    "completed_pomodoros": stats_data.get("completed_pomodoros", 0),
                    "interrupted_count": stats_data.get("interrupted_count", 0)
                }
            else:
                # Initialize with default structure
                self._stats = {
                    "daily": {},
                    "weekly": {},
                    "completed_pomodoros": 0,
                    "interrupted_count": 0
                }
                
        except Exception:
            # If loading fails, start with empty statistics
            self._stats = {
                "daily": {},
                "weekly": {},
                "completed_pomodoros": 0,
                "interrupted_count": 0
            }
    
    def _save_stats(self) -> None:
        """
        Save statistics to storage.
        
        Internal method called when statistics are modified.
        Preserves other data fields in storage.
        """
        try:
            # Load existing data to preserve other fields
            data = self.storage.load()
            
            # Update statistics
            data["statistics"] = self._stats
            
            # Save back to storage
            self.storage.save(data)
            
        except Exception:
            # Silently fail if save fails
            pass
