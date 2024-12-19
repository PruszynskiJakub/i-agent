import os
from typing import Optional


class FileRepository:
    """Repository for handling basic file system operations"""

    def __init__(self, base_path: str = "_uploads"):
        """
        Initialize FileRepository
        
        Args:
            base_path: Base directory for file storage (default: "_uploads")
        """
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)

    def save(self, content: str, filename: str) -> bool:
        """
        Save content to a file
        
        Args:
            content: Content to write to the file
            filename: Name of the file to save
            
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            full_path = os.path.join(self.base_path, filename)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
            
        except Exception:
            return False

    def read(self, filename: str) -> Optional[str]:
        """
        Read content from a file
        
        Args:
            filename: Name of the file to read
            
        Returns:
            Optional[str]: File contents if successful, None if file doesn't exist or error occurs
        """
        try:
            full_path = os.path.join(self.base_path, filename)
            
            if not os.path.exists(full_path):
                return None
                
            with open(full_path, 'r', encoding='utf-8') as f:
                return f.read()
                
        except Exception:
            return None

    def exists(self, filename: str) -> bool:
        """
        Check if a file exists
        
        Args:
            filename: Name of the file to check
            
        Returns:
            bool: True if file exists, False otherwise
        """
        full_path = os.path.join(self.base_path, filename)
        return os.path.exists(full_path)
