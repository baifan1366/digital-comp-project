"""
Dialog windows and notification popups for the Study Planner.

Provides popup notifications for phase transitions and settings dialogs
for notification preferences.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional


class NotificationPopup:
    """
    Popup notification dialog for phase transitions.
    
    Displays modal or non-modal notifications when study phases change.
    """
    
    @staticmethod
    def show_study_start(parent: Optional[tk.Widget] = None) -> None:
        """
        Show notification that study period has started.
        
        Args:
            parent: Parent widget for the dialog (optional)
        """
        messagebox.showinfo(
            "Study Time",
            "Time to study! Focus on your work.",
            parent=parent
        )
    
    @staticmethod
    def show_break_start(parent: Optional[tk.Widget] = None) -> None:
        """
        Show notification that break period has started.
        
        Args:
            parent: Parent widget for the dialog (optional)
        """
        messagebox.showinfo(
            "Break Time",
            "Take a break! Relax and recharge.",
            parent=parent
        )
    
    @staticmethod
    def show_long_break_start(parent: Optional[tk.Widget] = None) -> None:
        """
        Show notification that long break has started.
        
        Args:
            parent: Parent widget for the dialog (optional)
        """
        messagebox.showinfo(
            "Long Break",
            "Time for a long break! You've earned it.",
            parent=parent
        )
    
    @staticmethod
    def show_session_complete(parent: Optional[tk.Widget] = None) -> None:
        """
        Show notification that session is complete.
        
        Args:
            parent: Parent widget for the dialog (optional)
        """
        messagebox.showinfo(
            "Session Complete",
            "Great job! Your study session is complete.",
            parent=parent
        )


class NotificationSettingsDialog:
    """
    Dialog for configuring notification preferences.
    
    Allows users to enable/disable different notification channels:
    - Popup notifications
    - System notifications
    - Sound alerts
    """
    
    def __init__(
        self,
        parent: tk.Widget,
        popup_enabled: bool = True,
        system_enabled: bool = True,
        sound_enabled: bool = True
    ):
        """
        Initialize the notification settings dialog.
        
        Args:
            parent: Parent widget for the dialog
            popup_enabled: Initial state of popup notifications
            system_enabled: Initial state of system notifications
            sound_enabled: Initial state of sound alerts
        """
        self.parent = parent
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Notification Settings")
        self.dialog.geometry("400x250")
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.dialog.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.dialog.winfo_height() // 2)
        self.dialog.geometry(f"+{x}+{y}")
        
        # Build UI
        self._build_ui(popup_enabled, system_enabled, sound_enabled)
    
    def _build_ui(
        self,
        popup_enabled: bool,
        system_enabled: bool,
        sound_enabled: bool
    ) -> None:
        """
        Build the settings dialog UI.
        
        Args:
            popup_enabled: Initial state of popup notifications
            system_enabled: Initial state of system notifications
            sound_enabled: Initial state of sound alerts
        """
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Notification Preferences",
            font=("Arial", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        # Popup notifications checkbox
        self.popup_var = tk.BooleanVar(value=popup_enabled)
        popup_check = ttk.Checkbutton(
            main_frame,
            text="Enable popup notifications",
            variable=self.popup_var
        )
        popup_check.grid(row=1, column=0, columnspan=2, pady=5, sticky=tk.W)
        
        popup_desc = ttk.Label(
            main_frame,
            text="Show notification dialogs within the application",
            font=("Arial", 9),
            foreground="gray"
        )
        popup_desc.grid(row=2, column=0, columnspan=2, padx=20, sticky=tk.W)
        
        # System notifications checkbox
        self.system_var = tk.BooleanVar(value=system_enabled)
        system_check = ttk.Checkbutton(
            main_frame,
            text="Enable system notifications",
            variable=self.system_var
        )
        system_check.grid(row=3, column=0, columnspan=2, pady=(15, 5), sticky=tk.W)
        
        system_desc = ttk.Label(
            main_frame,
            text="Show notifications using your operating system",
            font=("Arial", 9),
            foreground="gray"
        )
        system_desc.grid(row=4, column=0, columnspan=2, padx=20, sticky=tk.W)
        
        # Sound alerts checkbox
        self.sound_var = tk.BooleanVar(value=sound_enabled)
        sound_check = ttk.Checkbutton(
            main_frame,
            text="Enable sound alerts",
            variable=self.sound_var
        )
        sound_check.grid(row=5, column=0, columnspan=2, pady=(15, 5), sticky=tk.W)
        
        sound_desc = ttk.Label(
            main_frame,
            text="Play audio alerts for phase transitions",
            font=("Arial", 9),
            foreground="gray"
        )
        sound_desc.grid(row=6, column=0, columnspan=2, padx=20, sticky=tk.W)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=7, column=0, columnspan=2, pady=(20, 0), sticky=(tk.E, tk.W))
        
        # Save button
        save_btn = ttk.Button(
            button_frame,
            text="Save",
            command=self._on_save
        )
        save_btn.grid(row=0, column=0, padx=5, sticky=tk.E)
        
        # Cancel button
        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        )
        cancel_btn.grid(row=0, column=1, padx=5, sticky=tk.E)
        
        button_frame.columnconfigure(0, weight=1)
        
        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        self.dialog.columnconfigure(0, weight=1)
        self.dialog.rowconfigure(0, weight=1)
    
    def _on_save(self) -> None:
        """Handle save button click."""
        self.result = {
            "popup_enabled": self.popup_var.get(),
            "system_enabled": self.system_var.get(),
            "sound_enabled": self.sound_var.get()
        }
        self.dialog.destroy()
    
    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[dict]:
        """
        Show the dialog and wait for user response.
        
        Returns:
            Dictionary with notification settings if saved, None if cancelled
        """
        self.dialog.wait_window()
        return self.result
