import os
from typing import Dict, Tuple

import resend

from llm.open_ai import completion
from models.document import Document, DocumentType
from utils.document import create_document, create_error_document


async def _send_email(params: Dict, span) -> Document:
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")

        # Extract parameters
        query = params.get("query", "")
        attachments = params.get("attachments", [])

        # Send email using resend with basic content
        subject = "Message from iAgent"
        html = f"<p>Message content: {query}</p>"
        result = resend.Emails.send({
            "from": "iagent@pruszyn.ski",
            "to": "jakub.mikolaj.pruszynski@gmail.com",
            "subject": subject,
            "html": html,
            attachments: [],
        })

        result_details = [
            "Email Send Results:",
            f"Subject: {subject}",
            f"Status: Success",
            f"Email ID: {result.id if hasattr(result, 'id') else 'Not available'}",
            f"Recipient: {params.get('to', 'jakub.mikolaj.pruszynski@gmail.com')}",
            f"Content Length: {len(html)} characters"
        ]

        return create_document(
            text="\n".join(result_details),
            metadata_override={
                "conversation_uuid": span.trace_id,
                "source": "resend",
                "name": "EmailSendResult",
                "description": f"Email sent: {subject}",
                "mime_type": "text/plain",
                "content_type": "full",
                "type": DocumentType.DOCUMENT
            }
        )

    except Exception as e:
        return create_error_document(
            error=e,
            error_context="Failed to send email",
            conversation_uuid=span.trace_id
        )

