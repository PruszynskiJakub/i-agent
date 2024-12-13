from typing import Dict, Any, List, Tuple
import re
from uuid import UUID
from modules.types import Document, DocumentMetadata

class TextService:
    """Service for processing and managing text documents"""
    
    def document(self, content: str, metadata: Dict[str, Any] = None) -> Document:
        """
        Creates a Document object from content and metadata
        
        Args:
            content: The text content to process
            metadata: Optional dictionary of metadata about the document
            
        Returns:
            Document object containing the content and metadata
        """
        if metadata is None:
            metadata = {}
            
        # Ensure metadata matches DocumentMetadata type
        document_metadata: DocumentMetadata = {
            "uuid": metadata.get("uuid", UUID(int=0)),
            "conversation_uuid": metadata.get("conversation_uuid", ""),
            "source": metadata.get("source", ""),
            "mime_type": metadata.get("mime_type", ""),
            "name": metadata.get("name", "")
        }
            
        return Document(
            text=content,
            metadata=document_metadata
        )
        
    def extract_images_and_urls(self, text: str) -> Dict[str, Any]:
        """
        Extracts image URLs and regular URLs from markdown text content, replacing them with placeholders
        
        Args:
            text: The markdown text content to process
            
        Returns:
            Dictionary containing:
                - content: Text with placeholders for images and URLs
                - images: List of extracted image URLs
                - urls: List of extracted regular URLs
        """
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
            return match.group(0)  # Keep image placeholders unchanged

        # Replace markdown images first
        content = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_images, content)
        
        # Then replace markdown links
        content = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', replace_urls, content)

        # Finally handle bare URLs
        def replace_bare_urls(match):
            nonlocal url_index
            url = match.group(0)
            if not url.startswith('{{$'):  # Skip if it's already a placeholder
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
