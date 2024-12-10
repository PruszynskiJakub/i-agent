import asyncio
from typing import Dict, Any
import aiohttp
from bs4 import BeautifulSoup
from modules.logging_service import log_tool_call

async def webscrape_tool(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Scrapes content from a given URL
    
    Args:
        params: Dictionary containing:
            - url: The URL to scrape
        
    Returns:
        Dict containing:
            - title: page title
            - text: main text content
            - status: HTTP status code
    """
    url = params.get('url')
    if not url:
        return {"error": "URL parameter is required", "status": 400}
        
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                html = await response.text()
                status = response.status
                
                soup = BeautifulSoup(html, 'html.parser')
                
                # Remove script and style elements
                for script in soup(["script", "style"]):
                    script.decompose()
                    
                # Get text content
                text = soup.get_text(separator=' ', strip=True)
                
                # Get title
                title = soup.title.string if soup.title else ''
                
                result = {
                    "title": title,
                    "text": text[:1000],  # Limit text length
                    "status": status
                }
                
                log_tool_call("webscrape_tool", {"url": url}, result)
                return result
                
        except Exception as e:
            error_result = {
                "error": str(e),
                "status": 500
            }
            log_tool_call("webscrape_tool", params, error_result)
            return error_result
