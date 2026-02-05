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