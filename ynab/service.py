from typing import Dict, Any, List

from document.types import Document
from document.utils import create_error_document
from ynab.internal.add_transaction import add_transaction


async def execute_ynab(action, params: Dict[str, Any], trace) -> List[Document]:
    try:
        match action:
            case "add_transaction":
                result = await add_transaction(params, trace)
                return [result]
            case _:
                return [create_error_document(
                    Exception("Action not recognized"),
                    f"YNAB service received unknown action: {action}",
                    params.get("conversation_uuid", "")
                )]
    except Exception as e:
        return [create_error_document(
            e,
            f"Error executing YNAB action: {action}",
            params.get("conversation_uuid", "")
        )]
