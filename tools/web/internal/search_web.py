import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List

import aiohttp

from llm.open_ai import completion
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from models.document import Document, DocumentType
from utils.document import create_document

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

    async def build_queries() -> List[Dict]:
        """Build enhanced search queries using LLM return a list of queries in format {'q':'Query', 'url': 'URL'}"""
        prompt = get_prompt("tool_websearch_queries")
        model = prompt.get("model", "gpt-4o")

        system_prompt = prompt.compile(
            allowed_domains="\n".join([f"- {d['name']}: {d['url']}" for d in allowed_domains]),
            current_date=datetime.now().strftime("%Y-%m-%d")
        )

        generation = create_generation(
            span,
            "build_queries",
            model,
            system_prompt
        )

        result = await completion(
            [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model,
            json_mode=True
        )
        end_generation(generation, result)

        return json.loads(result)

    async def search(q) -> Dict:
        url = "https://google.serper.dev/search"
        payload = {
            "q": f"site:{q['url']} {q['query']}",
            "num": 5
        }
        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                response.raise_for_status()
                return await response.json()

    # Get enhanced queries from LLM
    queries = await build_queries()
    
    # Run all search queries in parallel
    search_tasks = [search(q) for q in queries]
    search_results = await asyncio.gather(*search_tasks)

    # Process results by query
    documents = []
    for query_info, results in zip(queries, search_results):
        # Collect all URLs from results
        urls = []
        text_parts = [f"Search Results for: {query_info['description']}\n"]
        
        for result in results.get('organic', []):
            urls.append(result.get('link', ''))
            text_parts.extend([
                f"\nTitle: {result.get('title', '')}",
                f"Snippet: {result.get('snippet', '')}",
                f"Link: {result.get('link', '')}"
            ])
            
        documents.append(create_document(
            text="\n".join(text_parts),
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "web",
                "name": "SearchWebResult",
                "description": f"Search results for: query {query_info['q']} for domain {query_info['url']}",
                "content_type": "full",
                type: DocumentType.DOCUMENT,
            }
        ))
    
    return documents
