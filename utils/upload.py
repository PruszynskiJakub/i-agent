import os
import uuid
import requests
from typing import Dict, Any
from datetime import datetime

def process_attachments(message: Dict[str, Any]) -> None:
    """Process and save image and audio attachments from Slack messages"""
    
    # Create base upload directory if it doesn't exist
    base_upload_dir = os.path.join(os.getcwd(), "_upload")
    os.makedirs(base_upload_dir, exist_ok=True)
    
    if "files" not in message:
        return
        
    # Create date-based directory for today's files
    today = datetime.now().strftime("%Y%m%d")
    today_dir = os.path.join(base_upload_dir, today)
    os.makedirs(today_dir, exist_ok=True)
        
    for file in message["files"]:
        # Get original file extension
        _, ext = os.path.splitext(file["name"])
        
        # Generate UUID-based filename with original extension
        new_filename = f"{uuid.uuid4()}{ext}"
        save_path = os.path.join(today_dir, new_filename)
        
        # Download and save file
        try:
            url = file["url_private_download"] if "url_private_download" in file else file["url_private"]
            headers = {'Authorization': f'Bearer {os.environ.get("SLACK_BOT_TOKEN")}'}
            response = requests.get(url, headers=headers, stream=True)
            response.raise_for_status()
            with open(save_path, 'wb') as out_file:
                for chunk in response.iter_content(chunk_size=8192):
                    out_file.write(chunk)
        except Exception as e:
            print(f"Error saving file {new_filename}: {str(e)}")
