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
        # Regular expressions for matching markdown URLs and images
        md_image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'  # ![alt text](url)
        md_url_pattern = r'(?<!!)\[([^\]]*)\]\(([^)]+)\)'  # [text](url) but not starting with !
        bare_url_pattern = r'(?<!\]\()(https?://[^\s<>"]+|www\.[^\s<>"]+)(?!\))'  # URLs not in markdown syntax
        
        content = text
        images = []
        urls = []
        
        # Extract and replace markdown images
        for idx, match in enumerate(re.finditer(md_image_pattern, text)):
            full_match = match.group(0)
            image_url = match.group(2)
            images.append(image_url)
            content = content.replace(full_match, f"[IMAGE_{idx}]")
        
        # Extract and replace markdown URLs
        for idx, match in enumerate(re.finditer(md_url_pattern, text)):
            full_match = match.group(0)
            url = match.group(2)
            urls.append(url)
            content = content.replace(full_match, f"[URL_{idx}]")
            
        # Extract and replace bare URLs
        bare_urls = re.findall(bare_url_pattern, content)
        for idx, url in enumerate(bare_urls, start=len(urls)):
            urls.append(url)
            content = content.replace(url, f"[URL_{idx}]")
            
        return {
            "content": content,
            "urls": urls,
            "images": images
        }
