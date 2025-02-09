from typing import Dict, List
from duckduckgo_search import DDGS

from models.document import Document, DocumentType
from utils.document import create_document

async def search(params: Dict, span) -> List[Document]:
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
    
    results = DDGS().text(
        query,
        region='wt-wt',
        safesearch='off', 
        timelimit='y',
        max_results=max_results
    )
    
    documents = []
    for result in results:
        # Create document for each search result
        doc_text = f"Title: {result['title']}\nURL: {result['link']}\n\n{result['body']}"
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
