import os
from typing import Dict, Any
import uuid
from firecrawl import FirecrawlApp
from modules.logging_service import log_tool_call
from modules.types import WebContent, Document

class WebService:
    def __init__(self, api_key: str, text_service, db_service):
        """
        Initialize WebService
        
        Args:
            api_key: Firecrawl API key
            text_service: TextService instance for document processing
            db_service: DatabaseService instance for storing documents
        """
        self.api_key = api_key
        self.app = FirecrawlApp(api_key=api_key)
        self.text_service = text_service
        self.db_service = db_service

    async def scrape_url(self, params: Dict[str, Any], conversation_uuid: str = None) -> Document:
        """
        Scrapes content from a URL and returns it as a Document
        
        Args:
            params: Dictionary containing:
                - url: The URL to scrape
                - format: Format to return ('md' or 'html')
            conversation_uuid: Optional UUID of the conversation context
            
        Returns:
            Document object containing the scraped content and metadata
        """
        web_content = await self._scrape_webpage(params)
        
        # Process content to extract images and URLs
        processed_content = self.text_service.extract_images_and_urls(web_content.content)
        
        # Create document metadata
        metadata = {
            "uuid": str(uuid.uuid4()),
            "source": web_content.url,
            "mime_type": "text/markdown" if web_content.type == 'md' else "text/html",
            "name": web_content.url.split('/')[-1] or "webpage",
            "conversation_uuid": conversation_uuid,
            "urls": processed_content["urls"],
            "images": processed_content["images"],
            "description": f"The content of the webpage {web_content.url}"
        }
        
        # Transform WebContent into Document using TextService
        document = self.text_service.document(
            content=processed_content["content"],
            metadata=metadata
        )
        
        # Store document in database
        document['metadata']['uuid'] = self.db_service.store_document(document)
        
        return document
    
    async def _scrape_webpage(self, params: Dict[str, Any]) -> WebContent:
        """
        Internal method to scrape raw content from a webpage
        
        Args:
            params: Dictionary containing:
                - url: The URL to scrape
                - format: Format to return ('md' or 'html')
            
        Returns:
            WebContent object with raw scraped content
        """
        url = params.get('url')
        format_type = params.get('format', 'md')  # Default to markdown
        
        if not url:
            raise ValueError("URL parameter is required")
            
        if format_type not in ['md', 'html']:
            raise ValueError("Format must be 'md' or 'html'")
            
        try:
            formats = ['markdown'] if format_type == 'md' else ['html']
            data = self.app.scrape_url(url, params={'formats': formats})
            content = data.get('markdown' if format_type == 'md' else 'html', '')
            
            web_content = WebContent(
                url=url,
                content=content,
                type=format_type
            )
            
            log_tool_call("scrape_url", params, {"status": "success", "content_length": len(content)})
            return web_content
            
        except Exception as e:
            log_tool_call("scrape_url", params, {"error": str(e)})
            raise
