import os
import json
from typing import Dict, List
import requests

from models.document import Document, DocumentType
from utils.document import create_document

# Predefined list of allowed domains with metadata for filtering search results
allowed_domains = [
    {"name": "Wikipedia", "url": "wikipedia.org", "type": "encyclopedia", "priority": 1},
    {"name": "Anthropic", "url": "anthropic.com", "type": "ai_company", "priority": 2},
    {"name": "OpenAI", "url": "openai.com", "type": "ai_company", "priority": 2}
]

async def _search(params: Dict, span) -> List[Document]:
    """Perform web search using DuckDuckGo
    
    Args:
        params: Dictionary containing search parameters
        span: Tracing span
        
    Returns:
        List of documents containing search results
    """
    query = params.get('query')
    if not query:
        raise ValueError("Search query is required")
        
    max_results = params.get('max_results', 10)
    
    # Add domain filtering using predefined allowed domains
    domain_query = ' OR '.join(f'site:{domain["url"]}' for domain in allowed_domains)
    search_query = f'({query}) ({domain_query})'
    
    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": search_query,
        "num": max_results
    })
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }

    response = requests.post(url, headers=headers, data=payload)
    response.raise_for_status()
    search_results = response.json()

    documents = []
    for result in search_results.get('organic', []):
        # Create document for each search result
        snippet = result.get('snippet', '')
        doc_text = f"Title: {result['title']}\nURL: {result['link']}\n\n{snippet}"
        doc = create_document(
            text=doc_text,
            metadata_override={
                "type": DocumentType.WEB_SEARCH,
                "url": result['link'],
                "title": result['title']
            }
        )
        documents.append(doc)
        
    return documents
