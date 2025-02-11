from typing import Dict, List, Any

from models.document import Document
from tools.web.internal.scrape import _scrape
from tools.web.internal.search_web import _search_web
from utils.document import create_error_document

async def execute_web(action: str, params: Dict[str, Any], span) -> List[Document]:
    """Execute web-related actions like scraping and searching

    Args:
        action: The action to perform (e.g. "scrape", "search")
        params: Parameters for the action
        span: Tracing span

    Returns:
        List of documents with results or error document if operation fails
    """
    try:
        if action == "scrape":
            result = await _scrape(params, span)
            return [result]
        elif action == "search":
            return await _search_web(params, span)
        else:
            return [
                create_error_document(
                    Exception(f"Unknown action: {action}"),
                    f"Web service received unknown action",
                    params.get("conversation_uuid", "")
                )
            ]
    except Exception as exception:
        return [
            create_error_document(
                exception,
                f"Error executing web action: {action}",
                params.get("conversation_uuid", "")
            )
        ]
