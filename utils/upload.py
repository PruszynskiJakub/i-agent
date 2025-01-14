import os
import uuid
import urllib.request
from typing import Dict, Any
from datetime import datetime

def process_attachments(message: Dict[str, Any]) -> None:
    """Process and save image and audio attachments from Slack messages"""
    
    # Create base upload directory if it doesn't exist
    base_upload_dir = os.path.join(os.getcwd(), "_upload")
    os.makedirs(base_upload_dir, exist_ok=True)
    
    # Create date-based directory
    today = datetime.now().strftime("%Y%m%d")
    upload_dir = os.path.join(base_upload_dir, today)
    os.makedirs(upload_dir, exist_ok=True)
    
    if "files" not in message:
        return
        
    for file in message["files"]:
        # Get original file extension
        _, ext = os.path.splitext(file["name"])
        
        # Generate UUID-based filename with original extension
        new_filename = f"{uuid.uuid4()}{ext}"
        save_path = os.path.join(upload_dir, new_filename)
        
        # Download and save file
        try:
            url = file["url_private_download"] if "url_private_download" in file else file["url_private"]
            headers = {'Authorization': f'Bearer {os.environ.get("SLACK_BOT_TOKEN")}'}
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req) as response, open(save_path, 'wb') as out_file:
                out_file.write(response.read())
        except Exception as e:
            print(f"Error saving file {new_filename}: {str(e)}")
