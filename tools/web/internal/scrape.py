import os
from typing import Dict
import aiohttp

from models.document import Document
from utils.document import create_document

async def scrape(params: Dict, span) -> Document:
    """Scrape content from a web page using Jina API

    Args:
        params: Dictionary containing:
            - url: URL to scrape
        span: Tracing span

    Returns:
        Document containing the scraped content
    """
    url = params.get("url")
    if not url:
        raise ValueError("URL is required for web scraping")

    jina_api_key = os.getenv("JINA_API_KEY")
    if not jina_api_key:
        raise ValueError("JINA_API_KEY environment variable is required")

    jina_url = f'https://r.jina.ai/{url}'
    headers = {
        'Authorization': f'Bearer {jina_api_key}'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(jina_url, headers=headers) as response:
            if response.status != 200:
                raise ValueError(f"Failed to scrape URL: {url}. Status: {response.status}")
            text = await response.text()

    metadata = {
        "source_url": url
    }

    return create_document(text, metadata)
