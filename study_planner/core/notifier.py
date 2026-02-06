"""
Notification system for study session phase transitions.

This module provides the Notifier class which delivers alerts through multiple
channels (popup, system notifications, and sound) when study phases transition.
"""

import logging
from typing import Optional

# Optional imports with graceful fallback
try:
    from plyer import notification as plyer_notification
    PLYER_AVAILABLE = True
except ImportError:
    PLYER_AVAILABLE = False

# Try to import winsound for Windows sound alerts
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

# Set up logging
logger = logging.getLogger(__name__)


class Notifier:
    """
    Manages notifications for study session phase transitions.
    
    Supports three notification channels:
    - Popup: In-app notifications
    - System: OS-level notifications
    - Sound: Audio alerts
    
    Each channel can be independently enabled or disabled.
    """
    
    def __init__(
        self,
        popup_enabled: bool = True,
        system_enabled: bool = True,
        sound_enabled: bool = True,
        sound_file: Optional[str] = None
    ):
        """
        Initialize the Notifier with channel preferences.
        
        Args:
            popup_enabled: Enable popup notifications (default: True)
            system_enabled: Enable system notifications (default: True)
            sound_enabled: Enable sound alerts (default: True)
            sound_file: Path to sound file for alerts (optional, not used on Windows)
        """
        self._popup_enabled = popup_enabled
        self._system_enabled = system_enabled
        self._sound_enabled = sound_enabled
        self._sound_file = sound_file
        
        # Log availability of notification systems
        if system_enabled and not PLYER_AVAILABLE:
            logger.warning("System notifications requested but plyer library not available")
        
        if sound_enabled and not WINSOUND_AVAILABLE:
            logger.warning("Sound alerts requested but winsound not available (non-Windows platform)")
    
    def notify_study_start(self) -> None:
        """
        Notify user that a study period has started.
        
        Sends notification through all enabled channels indicating
        that break time has ended and study time has begun.
        """
        message = "Study time has started!"
        self._send_notification(message)
    
    def notify_break_start(self) -> None:
        """
        Notify user that a break period has started.
        
        Sends notification through all enabled channels indicating
        that study time has ended and break time has begun.
        """
        message = "Break time has started!"
        self._send_notification(message)
    
    def notify_long_break_start(self) -> None:
        """
        Notify user that a long break period has started.
        
        Sends notification through all enabled channels indicating
        that a long break has begun.
        """
        message = "Long break has started!"
        self._send_notification(message)
    
    def notify_session_complete(self) -> None:
        """
        Notify user that the study session is complete.
        
        Sends notification through all enabled channels indicating
        that all cycles have been completed.
        """
        message = "Session complete! Great work!"
        self._send_notification(message)
    
    def set_popup_enabled(self, enabled: bool) -> None:
        """
        Enable or disable popup notifications.
        
        Args:
            enabled: True to enable popup notifications, False to disable
        """
        self._popup_enabled = enabled
    
    def set_system_enabled(self, enabled: bool) -> None:
        """
        Enable or disable system notifications.
        
        Args:
            enabled: True to enable system notifications, False to disable
        """
        self._system_enabled = enabled
    
    def set_sound_enabled(self, enabled: bool) -> None:
        """
        Enable or disable sound alerts.
        
        Args:
            enabled: True to enable sound alerts, False to disable
        """
        self._sound_enabled = enabled
    
    def _send_notification(self, message: str) -> None:
        """
        Send notification through all enabled channels.
        
        This is a placeholder implementation that will be extended
        with actual notification delivery mechanisms.
        
        Args:
            message: The notification message to send
        """
        if self._popup_enabled:
            self._send_popup(message)
        
        if self._system_enabled:
            self._send_system_notification(message)
        
        if self._sound_enabled:
            self._play_sound()
    
    def _send_popup(self, message: str) -> None:
        """
        Send popup notification (placeholder implementation).
        
        Args:
            message: The notification message to display
        """
        # Placeholder: Will be implemented with actual UI framework
        pass
    
    def _send_system_notification(self, message: str) -> None:
        """
        Send system notification using plyer library.
        
        Falls back gracefully if plyer is not available or if the
        notification system is unavailable on the current platform.
        
        Args:
            message: The notification message to display
        """
        if not PLYER_AVAILABLE:
            logger.debug("Skipping system notification: plyer not available")
            return
        
        try:
            plyer_notification.notify(
                title="Study Planner",
                message=message,
                app_name="Study Planner",
                timeout=5  # Notification displays for 5 seconds
            )
        except Exception as e:
            # Gracefully handle any notification errors
            logger.warning(f"Failed to send system notification: {e}")
    
    def _play_sound(self) -> None:
        """
        Play sound alert using system beep.
        
        On Windows, uses winsound.Beep() to generate a simple tone.
        Falls back gracefully on non-Windows platforms.
        """
        if not WINSOUND_AVAILABLE:
            logger.debug("Skipping sound alert: winsound not available (non-Windows platform)")
            return
        
        try:
            # Play a pleasant notification beep: 1000 Hz for 300ms
            winsound.Beep(1000, 300)
        except RuntimeError as e:
            logger.warning(f"Failed to play sound alert: {e}")
    
    def _fallback_beep(self) -> None:
        """
        Fallback to system beep when sound file is unavailable.
        This method is kept for compatibility but now just calls _play_sound.
        """
        self._play_sound()
