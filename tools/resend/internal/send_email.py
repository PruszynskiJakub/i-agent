import os
import resend
from typing import Dict, Tuple
from models.document import Document, DocumentType
from utils.document import create_document, create_error_document
from llm.open_ai import completion

async def _generate_email_content(query: str, span) -> Tuple[str, str]:
    """Generate email subject and content from natural language query"""
    messages = [
        {"role": "system", "content": """You are an email composer. Given a description, create an email with:
1. A clear, concise subject line
2. Professional HTML-formatted content
Return only valid JSON in this format:
{
    "subject": "Subject line here",
    "html": "HTML content here"
}"""},
        {"role": "user", "content": query}
    ]
    
    result = await completion(messages=messages, json_mode=True)
    return result["subject"], result["html"]

async def _send_email(params: Dict, span) -> Document:
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")
        
        # Extract parameters
        query = params.get("query", "")
        attachments = params.get("attachments", [])
        
        # Generate email content from query
        subject, html = await _generate_email_content(query, span)
        
        # Send email using resend
        result = resend.Emails.send({
            "from": "iagent@pruszyn.ski",
            "to": "jakub.mikolaj.pruszynski@gmail.com",
            "subject": subject,
            "html": html,
            # TODO: Handle attachments based on UUIDs
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
