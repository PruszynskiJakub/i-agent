from typing import List
from tools.resend.internal.send_email import _send_email
from models.document import Document

async def execute_resend(action: str, params: dict, span) -> List[Document]:
    if action == "send_email":
        result = await _send_email(params, span)
        return [result]
    
    raise ValueError(f"Unknown action {action} for resend tool")
