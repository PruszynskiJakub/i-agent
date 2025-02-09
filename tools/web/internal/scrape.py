from typing import Dict
import aiohttp
from bs4 import BeautifulSoup

from models.document import Document
from utils.document import create_document

async def scrape(params: Dict, span) -> Document:
    """Scrape content from a web page

    Args:
        params: Dictionary containing:
            - url: URL to scrape
            - selector: Optional CSS selector to target specific content
        span: Tracing span

    Returns:
        Document containing the scraped content
    """
    url = params.get("url")
    selector = params.get("selector")

    if not url:
        raise ValueError("URL is required for web scraping")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()
            
    soup = BeautifulSoup(html, 'html.parser')
    
    if selector:
        content = soup.select(selector)
        text = "\n".join(element.get_text(strip=True) for element in content)
    else:
        text = soup.get_text(strip=True)

    metadata = {
        "source_url": url,
        "selector": selector
    }

    return create_document(text, metadata)
