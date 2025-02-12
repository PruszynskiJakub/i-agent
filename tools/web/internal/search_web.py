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
    {"name": "OpenAI", "url": "openai.com"},
    {"name": "OpenAINews", "url": "openai.com/news"},
    {"name": "AnthropicNews", "url": "anthropic.com/news"}
]


async def _search_web(params: Dict, span) -> List[Document]:
    """Perform web search using DuckDuckGo
    
    Args:
        params: Dictionary containing search parameters
        span: Tracing span
        
    Returns:
        List of documents containing search results
    """
    user_query = params.get('query')
    if not user_query:
        raise ValueError("Search query is required")

    search_queries = await _build_queries(user_query, span)

    search_tasks = [_search(search_query) for search_query in search_queries['queries']]
    search_results = await asyncio.gather(*search_tasks, return_exceptions=True)

    picked_results = await _pick_relevant(search_results, user_query)

    scrape_tasks = [_scrape(url) for url in picked_results['urls']]
    scrape_results = await asyncio.gather(*scrape_tasks, return_exceptions=True)

    documents = []
    for query_info, results in zip(search_queries['queries'], search_results):
        # Collect all URLs from results
        urls = []
        text_parts = [f"Search Results for: {query_info['q']}\n"]

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
                "type": DocumentType.DOCUMENT,
            }
        ))

    return documents


async def _build_queries(user_query: str, span) -> Dict:
    """Build enhanced search queries using LLM return a list of queries in format {'q':'Query', 'url': 'URL'}"""
    prompt = get_prompt("tool_websearch_queries")
    model = prompt.config.get("model", "gpt-4o")

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
            {"role": "user", "content": user_query}
        ],
        model,
        json_mode=True
    )
    end_generation(generation, result)

    return json.loads(result)


async def _search(search_query) -> Dict:
    url = "https://google.serper.dev/search"
    payload = {
        "q": f"site:{search_query['url']} {search_query['q']}",
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


async def _pick_relevant(search_results, user_query, span) -> Dict:
    """Filter search results using an LLM to choose the few most correlated results
addressing the user query."""
    prompt = get_prompt("tool_websearch_pick")
    system_prompt = prompt.compile(
        search_results=json.dumps(search_results, indent=2),
        user_query=user_query
    )
    model = prompt.config.get("model", "gpt-4o")
    generation = create_generation(
        span,
        "pick_relevant",
        model,
        system_prompt
    )
    relevant_json = await completion(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ],
        model,
        json_mode=True
    )
    end_generation(generation, relevant_json)
    return json.loads(relevant_json)


async def _scrape(url) -> str:
    """Scrape content from the picked relevant URLs using the scraping service."""
    scrape_url = "https://scrape.serper.dev"
    headers = {
        'X-API-KEY': os.getenv("SERPER_API_KEY"),
        'Content-Type': 'application/json'
    }
    payload = json.dumps({"url": url})
    async with aiohttp.ClientSession() as session:
        async with session.post(scrape_url, headers=headers, json=payload) as response:
            response.raise_for_status()
            return await response.text()
