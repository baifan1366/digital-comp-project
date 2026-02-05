"""
Input validation utilities for the Study Planner application.

This module provides validation functions for user inputs including time parameters,
cycle counts, and numeric string parsing with appropriate error handling.
"""

from typing import Optional


def validate_time_input(minutes: int) -> bool:
    """
    Validate that time input is within acceptable range.
    
    Time inputs must be between 1 and 180 minutes inclusive for study time,
    break time, and long break time parameters.
    
    Args:
        minutes: The time value in minutes to validate
        
    Returns:
        bool: True if the time is valid (1-180 minutes), False otherwise
        
    Examples:
        >>> validate_time_input(25)
        True
        >>> validate_time_input(0)
        False
        >>> validate_time_input(181)
        False
    """
    return 1 <= minutes <= 180


def validate_cycle_count(cycles: int) -> bool:
    """
    Validate that cycle count is a positive integer.
    
    Cycle count must be at least 1 to represent a valid study session.
    
    Args:
        cycles: The number of study cycles to validate
        
    Returns:
        bool: True if the cycle count is valid (>= 1), False otherwise
        
    Examples:
        >>> validate_cycle_count(4)
        True
        >>> validate_cycle_count(0)
        False
        >>> validate_cycle_count(-1)
        False
    """
    return cycles >= 1


def validate_numeric_input(value: str) -> Optional[int]:
    """
    Parse and validate numeric string input.
    
    Attempts to parse a string as a positive integer. Returns None if the string
    is not a valid number or if the parsed number is not positive.
    
    Args:
        value: The string value to parse and validate
        
    Returns:
        Optional[int]: The parsed positive integer if valid, None otherwise
        
    Examples:
        >>> validate_numeric_input("25")
        25
        >>> validate_numeric_input("0")
        None
        >>> validate_numeric_input("-5")
        None
        >>> validate_numeric_input("abc")
        None
    """
    try:
        num = int(value)
        return num if num > 0 else None
    except ValueError:
        return None
