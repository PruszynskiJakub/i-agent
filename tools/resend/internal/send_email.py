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
            "to": "jakub.mikolaj.pruszynski@gmail.com",
            "subject": title,
            "html": text,
            # TODO: Handle attachments based on UUIDs
        })

        result_details = [
            "Email Send Results:",
            f"Subject: {title}",
            f"Status: Success",
            f"Email ID: {result.id if hasattr(result, 'id') else 'Not available'}",
            f"Recipient: {params.get('to', 'jakub.mikolaj.pruszynski@gmail.com')}",
            f"Content Length: {len(text)} characters"
        ]
        
        return create_document(
            text="\n".join(result_details),
            metadata_override={
                "conversation_uuid": span.trace_id,
                "source": "resend",
                "name": "EmailSendResult", 
                "description": f"Email sent: {title}",
                "mime_type": "text/plain"
            }
        )

    except Exception as e:
        return create_error_document(
            error=e,
            error_context="Failed to send email",
            conversation_uuid=span.trace_id
        )
