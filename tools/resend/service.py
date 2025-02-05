from tools.resend.internal.send_email import _send_email
from models.document import Document

async def execute_resend(action: str, params: dict, span) -> Document:
    if action == "send_email":
        return await _send_email(params, span)
    
    raise ValueError(f"Unknown action {action} for resend tool")
