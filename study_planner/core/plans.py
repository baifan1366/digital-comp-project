"""Study plan data models and management."""

from dataclasses import dataclass
from typing import List, Optional
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from study_planner.utils.validation import validate_time_input, validate_cycle_count
from study_planner.data.storage import Storage


@dataclass
class StudyPlan:
    """Represents a study session configuration.
    
    Attributes:
        name: Name of the study plan
        study_minutes: Duration of study periods in minutes
        break_minutes: Duration of break periods in minutes
        cycles: Number of study/break cycles (default: 1)
        long_break_minutes: Duration of long break after all cycles (default: 0)
    """
    
    name: str
    study_minutes: int
    break_minutes: int
    cycles: int = 1
    long_break_minutes: int = 0
    
    def to_dict(self) -> dict:
        """Serialize to dictionary for storage.
        
        Returns:
            Dictionary representation of the study plan
        """
        return {
            "name": self.name,
            "study_minutes": self.study_minutes,
            "break_minutes": self.break_minutes,
            "cycles": self.cycles,
            "long_break_minutes": self.long_break_minutes
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'StudyPlan':
        """Deserialize from dictionary.
        
        Args:
            data: Dictionary containing study plan data
            
        Returns:
            StudyPlan instance created from the dictionary
        """
        return StudyPlan(
            name=data["name"],
            study_minutes=data["study_minutes"],
            break_minutes=data["break_minutes"],
            cycles=data.get("cycles", 1),
            long_break_minutes=data.get("long_break_minutes", 0)
        )
    
    def __eq__(self, other) -> bool:
        """Compare plans for deduplication.
        
        Args:
            other: Another object to compare with
            
        Returns:
            True if plans have identical configuration, False otherwise
        """
        if not isinstance(other, StudyPlan):
            return False
        
        return (
            self.study_minutes == other.study_minutes
            and self.break_minutes == other.break_minutes
            and self.cycles == other.cycles
            and self.long_break_minutes == other.long_break_minutes
        )



class PlanManager:
    """
    Manages preset and custom study plans.
    
    Provides access to preset study plans (Pomodoro, Deep Focus, Light Review),
    custom plan creation with validation, and template storage for reusable
    custom plans.
    """
    
    # Preset plan configurations
    PRESET_POMODORO = StudyPlan(
        name="Pomodoro",
        study_minutes=25,
        break_minutes=5,
        cycles=4,
        long_break_minutes=15
    )
    
    PRESET_DEEP_FOCUS = StudyPlan(
        name="Deep Focus",
        study_minutes=50,
        break_minutes=10,
        cycles=1,
        long_break_minutes=0
    )
    
    PRESET_LIGHT_REVIEW = StudyPlan(
        name="Light Review",
        study_minutes=30,
        break_minutes=5,
        cycles=1,
        long_break_minutes=0
    )
    
    def __init__(self, storage: Optional[Storage] = None):
        """
        Initialize PlanManager with optional storage backend.
        
        Args:
            storage: Storage instance for persisting custom templates.
                    If None, templates will not be persisted.
        """
        self.storage = storage
        self._templates: List[StudyPlan] = []
        
        # Load templates from storage if available
        if self.storage:
            self._load_templates()
    
    def get_preset_plans(self) -> List[StudyPlan]:
        """
        Return list of preset study plans.
        
        Returns:
            List containing Pomodoro, Deep Focus, and Light Review presets
        """
        return [
            self.PRESET_POMODORO,
            self.PRESET_DEEP_FOCUS,
            self.PRESET_LIGHT_REVIEW
        ]
    
    def create_custom_plan(
        self,
        name: str,
        study_min: int,
        break_min: int,
        cycles: int = 1,
        long_break_min: int = 0
    ) -> StudyPlan:
        """
        Create and validate a custom study plan.
        
        Validates all time parameters and cycle count according to requirements.
        
        Args:
            name: Name for the custom plan
            study_min: Study duration in minutes (1-180)
            break_min: Break duration in minutes (1-180)
            cycles: Number of study/break cycles (>= 1, default: 1)
            long_break_min: Long break duration in minutes (0-180, default: 0)
            
        Returns:
            StudyPlan instance with validated parameters
            
        Raises:
            ValueError: If any parameter fails validation
        """
        # Validate study time
        if not validate_time_input(study_min):
            raise ValueError("Study time must be between 1 and 180 minutes")
        
        # Validate break time
        if not validate_time_input(break_min):
            raise ValueError("Break time must be between 1 and 180 minutes")
        
        # Validate cycle count
        if not validate_cycle_count(cycles):
            raise ValueError("Cycle count must be at least 1")
        
        # Validate long break time (0 is allowed for no long break)
        if long_break_min < 0 or long_break_min > 180:
            raise ValueError("Long break time must be between 0 and 180 minutes")
        
        return StudyPlan(
            name=name,
            study_minutes=study_min,
            break_minutes=break_min,
            cycles=cycles,
            long_break_minutes=long_break_min
        )
    
    def save_template(self, plan: StudyPlan) -> None:
        """
        Save a custom plan as a reusable template.
        
        Adds the plan to the templates list and persists to storage if available.
        Prevents duplicate templates based on plan equality.
        
        Args:
            plan: StudyPlan to save as template
        """
        # Check if template already exists (based on configuration, not name)
        if plan not in self._templates:
            self._templates.append(plan)
            
            # Persist to storage if available
            if self.storage:
                self._save_templates()
    
    def get_templates(self) -> List[StudyPlan]:
        """
        Load and return saved custom templates.
        
        Returns:
            List of custom study plan templates
        """
        return self._templates.copy()
    
    def _load_templates(self) -> None:
        """
        Load templates from storage.
        
        Internal method called during initialization.
        """
        if not self.storage:
            return
        
        try:
            data = self.storage.load()
            templates_data = data.get("templates", [])
            
            self._templates = [
                StudyPlan.from_dict(template_data)
                for template_data in templates_data
            ]
        except Exception:
            # If loading fails, start with empty templates
            self._templates = []
    
    def _save_templates(self) -> None:
        """
        Save templates to storage.
        
        Internal method called when templates are modified.
        """
        if not self.storage:
            return
        
        try:
            # Load existing data to preserve other fields
            data = self.storage.load()
            
            # Update templates
            data["templates"] = [
                template.to_dict()
                for template in self._templates
            ]
            
            # Save back to storage
            self.storage.save(data)
        except Exception:
            # Silently fail if save fails
            pass
