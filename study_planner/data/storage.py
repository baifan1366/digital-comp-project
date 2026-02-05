"""
Storage module for JSON-based data persistence.

Handles serialization, deserialization, and file I/O operations
with error handling for corrupted data and file permissions.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class Storage:
    """
    Handles JSON serialization and file I/O for persistent data storage.
    
    Provides methods to save, load, and check existence of JSON data files
    with comprehensive error handling for corrupted data and file permissions.
    """
    
    def __init__(self, file_path: str):
        """
        Initialize storage with a file path.
        
        Args:
            file_path: Path to the JSON storage file
        """
        self.file_path = Path(file_path)
    
    def save(self, data: Dict[str, Any]) -> None:
        """
        Serialize and save data to JSON file.
        
        Creates parent directories if they don't exist.
        Handles file permission errors gracefully.
        
        Args:
            data: Dictionary to serialize and save
            
        Raises:
            PermissionError: If file cannot be written due to permissions
            OSError: If file cannot be written due to other OS errors
        """
        try:
            # Create parent directories if they don't exist
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write JSON data to file with pretty formatting
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
                
        except PermissionError as e:
            raise PermissionError(f"Permission denied writing to {self.file_path}") from e
        except OSError as e:
            raise OSError(f"Error writing to {self.file_path}: {e}") from e
    
    def load(self) -> Dict[str, Any]:
        """
        Load and deserialize data from JSON file.
        
        Returns empty dictionary if file doesn't exist.
        Handles corrupted JSON gracefully by returning empty dictionary.
        
        Returns:
            Dictionary containing loaded data, or empty dict if file doesn't exist
            or is corrupted
            
        Raises:
            PermissionError: If file cannot be read due to permissions
        """
        # Return empty dict if file doesn't exist
        if not self.exists():
            return {}
        
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data if isinstance(data, dict) else {}
                
        except json.JSONDecodeError:
            # Corrupted JSON - backup the file and return empty dict
            self._backup_corrupted_file()
            return {}
        except PermissionError as e:
            raise PermissionError(f"Permission denied reading from {self.file_path}") from e
        except OSError:
            # Other file errors - return empty dict
            return {}
    
    def exists(self) -> bool:
        """
        Check if storage file exists.
        
        Returns:
            True if file exists, False otherwise
        """
        return self.file_path.exists() and self.file_path.is_file()
    
    def _backup_corrupted_file(self) -> None:
        """
        Create a backup of corrupted file with .bak extension.
        
        Internal method called when corrupted JSON is detected.
        Silently fails if backup cannot be created.
        """
        try:
            backup_path = self.file_path.with_suffix(self.file_path.suffix + '.bak')
            if self.file_path.exists():
                self.file_path.rename(backup_path)
        except (OSError, PermissionError):
            # Silently fail if backup cannot be created
            pass
