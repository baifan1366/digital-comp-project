"""Session state enumeration for study session management."""

from enum import Enum


class SessionState(Enum):
    """Defines all possible states of a study session."""
    
    IDLE = "idle"
    STUDY = "study"
    BREAK = "break"
    LONG_BREAK = "long_break"
    PAUSED = "paused"
    COMPLETED = "completed"
