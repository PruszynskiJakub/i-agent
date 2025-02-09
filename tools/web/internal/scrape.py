import os
from typing import Dict
import requests

from models.document import Document, DocumentType
from utils.document import create_document

async def _scrape(params: Dict, span) -> Document:
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

    response = requests.get(jina_url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Failed to scrape URL: {url}. Status: {response.status_code}")

    return create_document(
        text=response.text,
        metadata_override={
            "source": "web",
            "source_url": url,
            "mime_type": "text/markdown",
            "type": DocumentType.DOCUMENT,
            "name": "WebScrapeResult",
            "description": f"Web content scraped from {url}"
        }
    )
