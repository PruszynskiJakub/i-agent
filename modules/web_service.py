import os
from typing import Dict, Any
from firecrawl import FirecrawlApp
from modules.logging_service import log_tool_call
from modules.types import WebContent

class WebService:
    def __init__(self, api_key: str):
        """
        Initialize WebService
        
        Args:
            api_key: Firecrawl API key
        """
        self.api_key = api_key
        self.app = FirecrawlApp(api_key=api_key)

    async def scrape_url(self, params: Dict[str, Any]) -> WebContent:
        """
        Scrapes content from a given URL in specified format
        
        Args:
            params: Dictionary containing:
                - url: The URL to scrape
                - format: Format to return ('md' or 'html')
            
        Returns:
            WebContent object containing:
                - url: The scraped URL
                - content: scraped content in requested format
                - type: format type ('md' or 'html')
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
