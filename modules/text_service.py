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
        Extracts image URLs and regular URLs from text content, replacing them with placeholders
        
        Args:
            text: The text content to process
            
        Returns:
            Dictionary containing:
                - content: Text with placeholders for images and URLs
                - images: List of extracted image URLs
                - urls: List of extracted regular URLs
        """
        # Regular expressions for matching URLs and images
        url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+' 
        image_extensions = r'\.(jpg|jpeg|png|gif|bmp|webp|svg)($|\?)'
        
        # Find all URLs
        all_urls = re.findall(url_pattern, text)
        
        # Separate images from regular URLs
        images = [url for url in all_urls if re.search(image_extensions, url.lower())]
        urls = [url for url in all_urls if url not in images]
        
        # Replace URLs and images with placeholders
        content = text
        for idx, url in enumerate(urls):
            content = content.replace(url, f"[URL_{idx}]")
            
        for idx, img in enumerate(images):
            content = content.replace(img, f"[IMAGE_{idx}]")
            
        return {
            "content": content,
            "urls": urls,
            "images": images
        }
