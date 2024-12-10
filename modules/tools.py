from typing import Dict, Any
from firecrawl import AsyncCrawler
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
        
    try:
        crawler = AsyncCrawler()
        page = await crawler.crawl(url)
        
        if not page.success:
            error_result = {
                "error": "Failed to crawl page",
                "status": page.status_code or 500
            }
            log_tool_call("webscrape_tool", params, error_result)
            return error_result
            
        result = {
            "title": page.title,
            "text": page.text[:1000],  # Limit text length
            "status": page.status_code
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
