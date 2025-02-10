import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List

import aiohttp

from llm.open_ai import completion
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from models.document import Document

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
        """Build enhanced search queries using LLM"""
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
            "q": q,
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
    search_tasks = [search(variation["query"]) for variation in queries]
    search_results = await asyncio.gather(*search_tasks)
    
    # Flatten and process results
    documents = []
    for query_info, results in zip(queries, search_results):
        for result in results.get('organic', []):
            documents.append(Document(
                text=f"Query: {query_info['description']}\nTitle: {result.get('title', '')}\n"
                     f"Snippet: {result.get('snippet', '')}\nLink: {result.get('link', '')}",
                metadata={
                    "url": result.get('link'),
                    "title": result.get('title'),
                    "query": query_info['query'],
                    "reason": query_info['description']
                }
            ))
    
    return documents
