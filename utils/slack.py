import os
import uuid
from typing import Dict, Any, List

import requests
from models.document import DocumentType

from db.document import save_document
from logger.logger import log_info, log_error
from utils.document import create_document


def get_conversation_id(message: Dict[str, Any]) -> str:
    """Extract conversation ID from a Slack message"""
    return message.get("thread_ts", message.get("ts", ""))


def preprocess_message(message: Dict[str, Any], conversation_uuid: str) -> None:
    if "files" in message:
        _process_attachments(message['files'], conversation_uuid)


def _process_attachments(files: List[Dict[str, Any]], conversation_uuid) -> None:
    log_info(f"Processing {len(files)} files")

    for file in files:
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
                text=content,
                metadata_override={
                    'uuid': uuid.uuid4(),
                    "type": DocumentType.TEXT,
                    "source": url,
                    "mime_type": "text/markdown",
                    "name": file.get("title", file.get("name", "")),
                    "description": f"Markdown file from Slack: {file.get('title', '')}",
                    "conversation_uuid": conversation_uuid
                }
            )
            save_document(doc.__dict__)
            log_info(f"Created document record for: {file.get('title', '')}")

        except Exception as e:
            log_error(f"Error processing file {file.get('name', 'unknown')}: {str(e)}")
