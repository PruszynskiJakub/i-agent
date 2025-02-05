import os
import resend
from typing import Dict
from models.document import Document
from utils.document import create_document, create_error_document

async def _send_email(params: Dict, span) -> Document:
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        # Extract parameters
        title = params.get("title", "")
        text = params.get("text", "")
        attachments = params.get("attachments", [])
        
        # Send email using resend
        result = resend.Emails.send({
            "from": "notifications@yourdomain.com",  # Configure as needed
            "to": "recipient@example.com",  # Configure as needed
            "subject": title,
            "html": text,
            # TODO: Handle attachments based on UUIDs
        })

        return create_document(
            f"Email sent successfully with subject: {title}",
            {"email_id": result.id if hasattr(result, 'id') else None}
        )

    except Exception as e:
        return create_error_document(
            error=e,
            error_context="Failed to send email",
            conversation_uuid=span.trace_id
        )
