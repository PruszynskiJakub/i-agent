import os
import requests
from typing import Dict, Any, Optional
from utils.logger import log_info, log_error
from document.utils import create_document
from db.document import save_document
from document.types import DocumentType


def preprocess_message(message: Dict[str, Any]) -> None:
    """
    Preprocess a Slack message to extract and normalize relevant information.
    
    Args:
        message: Raw Slack message dictionary
    """
    pass


def get_conversation_id(message: Dict[str, Any]) -> str:
    """Extract conversation ID from a Slack message"""
    return message.get("thread_ts", message.get("ts", ""))


def process_attachments(message: Dict[str, Any]) -> None:
    """Process markdown files from Slack messages"""
    if "files" not in message:
        log_info("No files found in message")
        return
        
    log_info(f"Processing {len(message['files'])} files")
        
    for file in message["files"]:
        # Only process markdown files
        _, ext = os.path.splitext(file["name"])
        if ext.lower() not in ['.md', '.markdown']:
            continue
            
        try:
            # Get file URL and download content
            url = file.get("url_private", "")
            response = requests.get(
                url, 
                headers={'Authorization': f'Bearer {os.getenv("SLACK_BOT_TOKEN")}'}
            )
            response.raise_for_status()
            content = response.text
            
            # Create document record
            doc = create_document(
                content=content,
                metadata={
                    "type": DocumentType.TEXT,
                    "source": url,
                    "mime_type": "text/markdown",
                    "name": file.get("title", file.get("name", "")),
                    "description": f"Markdown file from Slack: {file.get('title', '')}",
                    "conversation_uuid": get_conversation_id(message)
                }
            )
            save_document(doc.__dict__)
            log_info(f"Created document record for: {file.get('title', '')}")
            
        except Exception as e:
            log_error(f"Error processing file {file.get('name', 'unknown')}: {str(e)}")
