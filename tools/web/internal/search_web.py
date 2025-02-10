import os
import json
from typing import Dict, List
import requests

from models.document import Document, DocumentType
from utils.document import create_document
from llm.prompts import get_prompt
from llm.open_ai import completion

# Predefined list of allowed domains with metadata for filtering search results
allowed_domains = [
    {"name": "Wikipedia", "url": "wikipedia.org"},
    {"name": "Anthropic", "url": "anthropic.com"},
    {"name": "OpenAI", "url": "openai.com"}
]

async def _search_web(params: Dict, span) -> List[Document]:
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

    async def build_queries() -> List[Dict]:
        """Build enhanced search queries using LLM"""
        from datetime import datetime
        from llm.tracing import create_generation, end_generation

        prompt = get_prompt("tool_searchweb_queries")
        formatted_domains = "\n".join([f"- {d['name']}: {d['url']}" for d in allowed_domains])
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        system_prompt = prompt.compile(
            allowed_domains=formatted_domains,
            current_date=current_date
        )
        
        generation = create_generation(
            span,
            "build_queries",
            prompt.config.get("model", "gpt-3.5-turbo"),
            system_prompt
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        response = await completion(messages, json_mode=True)
        end_generation(generation, response)
        
        return json.loads(response)

    # Get enhanced queries from LLM
    query_variations = await build_queries()
    
    documents = []
    for variation in query_variations:
        # Add domain filtering using predefined allowed domains
        domain_query = ' OR '.join(f'site:{domain["url"]}' for domain in allowed_domains)
        search_query = f'({variation["query"]}) ({domain_query})'
    
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
