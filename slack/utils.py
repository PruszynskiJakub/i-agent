from typing import Dict, Any, List
from document.types import DocumentType


async def preprocess_message(message: Dict[str, Any]) -> Dict[str, Any]:
    """
    Preprocess a Slack message to extract and normalize relevant information.
    
    Args:
        message: Raw Slack message dictionary
        
    Returns:
        Processed message with normalized fields
    """
    processed = {
        "text": message.get("text", ""),
        "conversation_id": message.get("thread_ts", message.get("ts", "")),
        "files": []
    }
    
    # Process any files in the message
    if "files" in message:
        for file in message["files"]:
            processed_file = {
                "id": file.get("id", ""),
                "name": file.get("title", file.get("name", "")),
                "mime_type": file.get("mimetype", ""),
                "url": file.get("url_private", ""),
                "download_url": file.get("url_private_download", ""),
                "size": file.get("size", 0),
                "type": DocumentType.TEXT  # Default type
            }
            
            # Determine document type based on mime_type
            mime_type = processed_file["mime_type"].lower()
            if mime_type.startswith("image/"):
                processed_file["type"] = DocumentType.IMAGE
            elif mime_type.startswith("audio/"):
                processed_file["type"] = DocumentType.AUDIO
            elif mime_type in ["text/markdown", "text/plain", "text/html"]:
                processed_file["type"] = DocumentType.TEXT
            else:
                processed_file["type"] = DocumentType.DOCUMENT
                
            processed["files"].append(processed_file)
            
    return processed
