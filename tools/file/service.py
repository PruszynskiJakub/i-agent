from typing import Dict, List

from models.document import Document
from tools.file.internal.summarize_file import _summarize_file
from utils.document import create_error_document


async def execute_file(action: str, params: Dict, span) -> List[Document]:
    """Execute file-related actions

    Args:
        action: The action to perform
        params: Parameters for the action
        span: Tracing span

    Returns:
        List[Document]: Documents resulting from the action
    """
    try:
        if action == "summarize":
            docs = await _summarize_file(params, span)
            return docs
        else:
            return [create_error_document(
                Exception(f"Unknown action: {action}"),
                f"File service received unknown action",
                params.get("conversation_uuid", "")
            )]
    except Exception as exception:
        return [create_error_document(
            exception,
            f"Error executing file action: {action}",
            params.get("conversation_uuid", "")
        )]
