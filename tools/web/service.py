from typing import Dict, List

from models.document import Document
from tools.web.internal.scrape import scrape

async def execute_web(action: str, params: Dict, span) -> List[Document]:
    """Execute web-related actions like scraping

    Args:
        action: The action to perform (e.g. "scrape")
        params: Parameters for the action
        span: Tracing span

    Returns:
        List of documents with results
    """
    if action == "scrape":
        result = await scrape(params, span)
        return [result]
    
    raise ValueError(f"Unknown web action: {action}")
