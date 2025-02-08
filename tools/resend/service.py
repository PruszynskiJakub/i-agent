from typing import List
from tools.resend.internal.send_email import _send_email
from models.document import Document
from utils.document import create_error_document

async def execute_resend(action: str, params: dict, span) -> List[Document]:
    try:
        if action == "send_email":
            result = await _send_email(params, span)
            return [result]
        else:
            return [
                create_error_document(
                    Exception(f"Unknown action: {action}"),
                    f"Resend service received unknown action",
                    params.get("conversation_uuid", "")
                )
            ]
    except Exception as exception:
        return [
            create_error_document(
                exception,
                f"Error executing Resend action: {action}",
                params.get("conversation_uuid", "")
            )
        ]
