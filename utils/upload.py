import os
import urllib.request
from typing import Dict, Any
from datetime import datetime

def process_attachments(message: Dict[str, Any]) -> None:
    """Process and save image and audio attachments from Slack messages"""
    
    # Create upload directory if it doesn't exist
    upload_dir = os.path.join(os.getcwd(), "_upload")
    os.makedirs(upload_dir, exist_ok=True)
    
    if "files" not in message:
        return
        
    for file in message["files"]:
        # Generate timestamp-based filename
        timestamp = datetime.fromtimestamp(int(float(file["created"])))
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        
        # Get original filename and extension
        original_name = file["name"]
        _, ext = os.path.splitext(original_name)
        
        # Create new filename with timestamp
        new_filename = f"{timestamp_str}_{original_name}"
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
