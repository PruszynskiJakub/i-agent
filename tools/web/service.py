from typing import Dict, List

from models.document import Document
from tools.web.internal.scrape import scrape
from tools.web.internal.search import search

async def execute_web(action: str, params: Dict, span) -> List[Document]:
    """Execute web-related actions like scraping and searching

    Args:
        action: The action to perform (e.g. "scrape", "search")
        params: Parameters for the action
        span: Tracing span

    Returns:
        List of documents with results
    """
    if action == "scrape":
        result = await scrape(params, span)
        return [result]
    elif action == "search":
        return await search(params, span)
    
    raise ValueError(f"Unknown web action: {action}")
