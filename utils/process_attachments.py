import os
import uuid
import requests
from typing import Dict, Any
from datetime import datetime
from utils.logger import log_info, log_error
from document.utils import create_document
from db.document import save_document

def get_conversation_id(message: Dict[str, Any]) -> str:
    """Extract conversation ID from a Slack message"""
    return message.get("thread_ts", message.get("ts", ""))

def process_attachments(message: Dict[str, Any]) -> None:
    """Process and save image and audio attachments from Slack messages"""
    
    # Create base upload directory if it doesn't exist
    base_upload_dir = os.path.join(os.getcwd(), "_upload")
    os.makedirs(base_upload_dir, exist_ok=True)

    if "files" not in message:
        log_info("No files found in message")
        return
        
    # Create date-based directory for today's files
    today = datetime.now().strftime("%Y%m%d")
    today_dir = os.path.join(base_upload_dir, today)
    os.makedirs(today_dir, exist_ok=True)
    log_info(f"Processing {len(message['files'])} files into directory: {today_dir}")
        
    for file in message["files"]:
        # Get original file extension
        _, ext = os.path.splitext(file["name"])
        
        # Generate UUID and filename
        file_uuid = uuid.uuid4()
        new_filename = f"{file_uuid}{ext}"
        save_path = os.path.join(today_dir, new_filename)
        
        # Download and save file 
        try:
            url = file["url_private_download"] if "url_private_download" in file else file["url_private"]
            log_info(f"Downloading file: {file['name']} -> {new_filename}")
            response = requests.get(url, stream=True, headers={'Authorization': f'Bearer {os.getenv("SLACK_BOT_TOKEN")}'})
            response.raise_for_status()
            with open(save_path, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)
            log_info(f"Successfully saved file: {new_filename}")
            
            # Create document for markdown files
            if ext.lower() in ['.md', '.markdown']:
                with open(save_path, 'r') as md_file:
                    content = md_file.read()
                    doc = create_document(
                        content=content,
                        metadata={
                            "uuid": file_uuid,
                            "source": save_path,
                            "mime_type": "text/markdown",
                            "name": file["name"],
                            "description": f"Markdown file uploaded from Slack: {file['name']}",
                            "conversation_uuid": get_conversation_id(message)
                        }
                    )
                    save_document(doc.__dict__)
                    log_info(f"Created document from markdown file: {file['name']}")
        except Exception as e:
            log_error(f"Error saving file {new_filename}: {str(e)}")
