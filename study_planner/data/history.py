"""
History management for study session configurations.

Tracks and retrieves recently used study plans with deduplication
and timestamp-based ordering.
"""

from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from study_planner.core.plans import StudyPlan
    from study_planner.data.storage import Storage


class HistoryManager:
    """
    Manages history of recently used study configurations.
    
    Provides functionality to track study plans with timestamps,
    deduplicate identical configurations, and retrieve recent entries
    sorted by most recent usage.
    """
    
    def __init__(self, storage: 'Storage', max_entries: int = 5):
        """
        Initialize HistoryManager with storage backend.
        
        Args:
            storage: Storage instance for persisting history data
            max_entries: Maximum number of history entries to maintain (default: 5)
        """
        self.storage = storage
        self.max_entries = max_entries
        self._history: List[dict] = []
        
        # Load existing history from storage
        self._load_history()
    
    def add_entry(self, plan: 'StudyPlan') -> None:
        """
        Add plan to history with deduplication logic.
        
        If an identical plan already exists in history (based on StudyPlan.__eq__),
        only the timestamp is updated. Otherwise, a new entry is added.
        Maintains max_entries limit by removing oldest entries.
        
        Args:
            plan: StudyPlan to add to history
        """
        from study_planner.core.plans import StudyPlan
        
        current_timestamp = datetime.now().isoformat()
        
        # Check if identical plan exists (based on configuration, not name)
        existing_index = None
        for i, entry in enumerate(self._history):
            existing_plan = StudyPlan.from_dict(entry["plan"])
            if existing_plan == plan:
                existing_index = i
                break
        
        if existing_index is not None:
            # Update timestamp of existing entry
            self._history[existing_index]["timestamp"] = current_timestamp
            # Update name in case it changed
            self._history[existing_index]["plan"]["name"] = plan.name
        else:
            # Add new entry
            new_entry = {
                "plan": plan.to_dict(),
                "timestamp": current_timestamp
            }
            self._history.append(new_entry)
        
        # Sort by timestamp (most recent first)
        self._history.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Limit to max_entries
        if len(self._history) > self.max_entries:
            self._history = self._history[:self.max_entries]
        
        # Persist to storage
        self._save_history()
    
    def get_recent(self, count: int = 5) -> List['StudyPlan']:
        """
        Get N most recent study plans.
        
        Returns plans sorted by most recent timestamp first.
        
        Args:
            count: Number of recent plans to retrieve (default: 5)
            
        Returns:
            List of StudyPlan instances, sorted by most recent first,
            limited to the requested count
        """
        from study_planner.core.plans import StudyPlan
        
        # History is already sorted by timestamp (most recent first)
        recent_entries = self._history[:min(count, len(self._history))]
        
        return [
            StudyPlan.from_dict(entry["plan"])
            for entry in recent_entries
        ]
    
    def clear(self) -> None:
        """
        Clear all history entries.
        
        Removes all history data from memory and persistent storage.
        """
        self._history = []
        self._save_history()
    
    def _load_history(self) -> None:
        """
        Load history from storage.
        
        Internal method called during initialization.
        Handles corrupted or missing data gracefully.
        """
        try:
            data = self.storage.load()
            history_data = data.get("history", [])
            
            # Validate that history_data is a list
            if isinstance(history_data, list):
                self._history = history_data
            else:
                self._history = []
                
        except Exception:
            # If loading fails, start with empty history
            self._history = []
    
    def _save_history(self) -> None:
        """
        Save history to storage.
        
        Internal method called when history is modified.
        Preserves other data fields in storage.
        """
        try:
            # Load existing data to preserve other fields
            data = self.storage.load()
            
            # Update history
            data["history"] = self._history
            
            # Save back to storage
            self.storage.save(data)
            
        except Exception:
            # Silently fail if save fails
            pass
