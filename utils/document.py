import re
from typing import Dict, Any, Optional
from uuid import UUID, uuid4

from models.document import Document, DocumentMetadata, DocumentType


def create_error_document(
    error: Exception,
    error_context: str,
    conversation_uuid: str,
    source_uuid: Optional[str] = None
) -> Document:
    """Creates a Document object from an error and its context

    Args:
        error: The exception that occurred
        error_context: Description of what was being attempted when the error occurred
        conversation_uuid: UUID of the conversation this error is associated with
        source_uuid: Optional UUID of the source document/operation that caused the error

    Returns:
        Document object containing error details
    """
    error_message = str(error)
    error_text = f"Error: {error_message}\nContext: {error_context}"

    return create_document(
        text=error_text,
        metadata_override={
            "conversation_uuid": conversation_uuid,
            "source_uuid": source_uuid or conversation_uuid,
            "mime_type": "text/plain",
            "name": "error_report", 
            "source": "system",
            "description": f"Failed to process operation: {error_message}",
            "content_type": "full",
            "type": DocumentType.DOCUMENT
        }
    )


def create_document(text: str, metadata_override: Dict[str, Any] = {}) -> Document:
    """Creates a Document object from content and metadata"""

    document_metadata: DocumentMetadata = {
        "type": metadata_override.get("type", DocumentType.DOCUMENT),
        "source": metadata_override.get("source", ""),
        "mime_type": metadata_override.get("mime_type", "text/plain"),
        "name": metadata_override.get("name", ""),
        "description": metadata_override.get("description", ""),
        "images": metadata_override.get("images", []),
        "urls": metadata_override.get("urls", [])
    }

    extracted_text = text
    if not document_metadata["images"] and not document_metadata["urls"]:
        extracted = extract_images_and_urls(text)
        document_metadata["images"] = extracted["images"]
        document_metadata["urls"] = extracted["urls"]
        extracted_text = extracted["content"]

    return Document(
        uuid=metadata_override.get("uuid", uuid4()),
        conversation_uuid=metadata_override.get("conversation_uuid", ""),
        text=extracted_text,
        metadata=document_metadata
    )


def restore_placeholders(doc: Document) -> Document:
    """Restores original URLs and images from placeholders in the document text"""
    content = doc.text
    metadata = doc.metadata

    urls = metadata.get("urls", [])
    images = metadata.get("images", [])

    # Restore image placeholders
    for i, image_url in enumerate(images):
        content = content.replace(f"{{$img{i}}}", image_url)

    # Restore URL placeholders
    for i, url in enumerate(urls):
        content = content.replace(f"{{$url{i}}}", url)

    return create_document(
        content,
        {
            "uuid": doc.uuid,
            "conversation_uuid": doc.conversation_uuid,
            **metadata
        }
    )


def extract_images_and_urls(text: str) -> Dict[str, Any]:
    """Extracts image URLs and regular URLs from markdown text content"""
    urls = []
    images = []
    url_index = 0
    image_index = 0
    content = text

    def replace_images(match):
        nonlocal image_index
        alt_text, url = match.groups()
        images.append(url)
        placeholder = f"![{alt_text}]({{$img{image_index}}})"
        image_index += 1
        return placeholder

    def replace_urls(match):
        nonlocal url_index
        link_text, url = match.groups()
        if not url.startswith('{{$img'):
            urls.append(url)
            placeholder = f"[{link_text}]({{$url{url_index}}})"
            url_index += 1
            return placeholder
        return match.group(0)

    # Replace markdown images first
    content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_images, content)

    # Then replace markdown links
    content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_urls, content)

    # Handle bare URLs
    def replace_bare_urls(match):
        nonlocal url_index
        url = match.group(0)
        if not url.startswith('{{$'):
            urls.append(url)
            placeholder = f"{{$url{url_index}}}"
            url_index += 1
            return placeholder
        return url

    content = re.sub(
        r'(?<!\]\()(https?://[^\s<>"]+|www\.[^\s<>"]+)(?!\))',
        replace_bare_urls,
        content
    )

    return {
        "content": content,
        "urls": urls,
        "images": images
    }
