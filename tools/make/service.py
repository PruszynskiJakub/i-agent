from typing import Dict, List, Any
from models.document import Document
from llm.tracing import create_span, end_span
from tools.make.internal.create_invoice import create_invoice

async def execute_make(action: str, params: Dict[str, Any], trace) -> List[Document]:
    """
    Execute the specified make action with the given parameters.
    
    Args:
        action: The action to execute
        params: The parameters for the action
        trace: The trace object for logging
    
    Returns:
        List[Document]: A list of documents resulting from the action
    """
    action_span = create_span(trace, f"make.{action}")
    
    try:
        if action == "invoice":
            document = await create_invoice(params, action_span)
            end_span(action_span, document)
            return [document]
        else:
            raise ValueError(f"Unknown make action: {action}")
    except Exception as e:
        end_span(action_span, {"error": str(e)}, "error")
        raise
