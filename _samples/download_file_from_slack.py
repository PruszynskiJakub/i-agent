import os
import requests

token = os.getenv("SLACK_APP_TOKEN")

def download_file(url: str, save_dir: str = '_upload') -> str:
    """
    Download a file from URL and save it to the specified directory
    Returns the path to the saved file
    """
    # Create upload directory if it doesn't exist
    os.makedirs(save_dir, exist_ok=True)
    
    # Extract filename from URL
    filename = url.split('/')[-1]
    save_path = os.path.join(save_dir, filename)
    
    # Download the file
    response = requests.get(url, stream=True, headers={"Authorization": f"Bearer {token}"})
    response.raise_for_status()  # Raise exception for bad status codes
    
    # Save the file
    with open(save_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            
    return save_path

if __name__ == "__main__":
    url = "https://files.slack.com/files-pri/T08593FTDPH-F088M84RAQ4/chatgpt_image.webp"
    try:
        saved_path = download_file(url)
        print(f"File successfully downloaded to: {saved_path}")
    except Exception as e:
        print(f"Error downloading file: {str(e)}")
