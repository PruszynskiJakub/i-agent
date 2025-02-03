from typing import Dict, Any, List

from models.document import Document
from tools.ynab.internal.add_transactions import _add_transactions
from tools.ynab.internal.update_transaction import _update_transaction
from utils.document import create_error_document


async def execute_ynab(action, params: Dict[str, Any], trace) -> List[Document]:
    try:
        match action:
            case "add_transaction":
                result = await _add_transactions(params, trace)
                return [result]
            case "update_transaction":
                result = await _update_transaction(params, trace)
                return [result]
            case _:
                return [
                    create_error_document(
                        error=ValueError("Action not recognized"),
                        error_context=f"YNAB service received unknown action: {action}",
                        conversation_uuid=params.get("conversation_uuid", "unknown")
                    )
                ]
    except Exception as exception:
        return [
            create_error_document(
                error=exception,
                error_context=f"Error executing YNAB action: {action}",
                conversation_uuid=params.get("conversation_uuid", "unknown")
            )
        ]
