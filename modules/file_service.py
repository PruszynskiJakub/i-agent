import os
from typing import Dict, Any
from modules.types import Document, ActionResult, ActionStatus
from modules.logging_service import log_info, log_error

class FileService:
    """Service for handling file system operations"""
    
    def __init__(self, base_path: str = "uploads"):
        """
        Initialize FileService
        
        Args:
            base_path: Base directory for file uploads (default: "uploads")
        """
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
        
    def upload(self, document: Document, path: str) -> ActionResult:
        """
        Upload a document to the file system
        
        Args:
            document: Document to upload
            path: Target path for the file
            
        Returns:
            ActionResult with status and result message
        """
        try:
            # Ensure the path is within base_path
            full_path = os.path.join(self.base_path, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            
            # Write the document content to file
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(document['content'])
                
            log_info(f"File uploaded successfully to {full_path}")
            
            return ActionResult(
                result={"message": f"File uploaded successfully to {path}"},
                status=ActionStatus.SUCCESS,
                documents=[]
            )
            
        except Exception as e:
            error_msg = f"Failed to upload file: {str(e)}"
            log_error(error_msg)
            
            return ActionResult(
                result={"error": error_msg},
                status=ActionStatus.ERROR,
                documents=[]
            )
