"""Time formatting utilities for the Study Planner application."""


def format_time(seconds: int) -> str:
    """
    Format seconds into MM:SS display format.
    
    Args:
        seconds: Total seconds to format
        
    Returns:
        String in MM:SS format (e.g., "25:00", "05:30", "00:45")
        
    Examples:
        >>> format_time(1500)
        '25:00'
        >>> format_time(330)
        '05:30'
        >>> format_time(45)
        '00:45'
        >>> format_time(0)
        '00:00'
    """
    if seconds < 0:
        seconds = 0
    
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    
    return f"{minutes:02d}:{remaining_seconds:02d}"


def format_duration(minutes: int) -> str:
    """
    Format minutes into human-readable duration string.
    
    Args:
        minutes: Duration in minutes
        
    Returns:
        Human-readable string (e.g., "25 minutes", "1 minute", "90 minutes")
        
    Examples:
        >>> format_duration(25)
        '25 minutes'
        >>> format_duration(1)
        '1 minute'
        >>> format_duration(0)
        '0 minutes'
        >>> format_duration(60)
        '60 minutes'
    """
    if minutes == 1:
        return "1 minute"
    return f"{minutes} minutes"
