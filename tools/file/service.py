from typing import Dict, List

from models.document import Document
from tools.file.internal.process_file import _process_file


async def execute_file(action: str, params: Dict, span) -> List[Document]:
    """Execute file-related actions

    Args:
        action: The action to perform
        params: Parameters for the action
        span: Tracing span

    Returns:
        List[Document]: Documents resulting from the action
    """
    if action == "process":
        return await _process_file(params, span)
    
    raise ValueError(f"Unknown file action: {action}")
