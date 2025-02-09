import os
import json
from typing import Dict, List
from uuid import UUID

import resend

from llm.open_ai import completion
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from models.document import Document, DocumentType
from utils.document import create_document, create_error_document, restore_placeholders
from db.document import find_document_by_uuid
from llm.format import format_documents, format_facts


async def _send_email(params: Dict, span) -> Document:
    try:
        resend.api_key = os.getenv("RESEND_API_KEY")

        # Extract required parameters
        query = params["query"]
        document_uuids = params["documents"]

        # Load and process documents
        documents: List[Document] = []
        for uuid_str in document_uuids:
            doc = find_document_by_uuid(UUID(uuid_str))
            if doc:
                doc = restore_placeholders(doc)
                documents.append(doc)
            else:
                raise ValueError(f"Document not found: {uuid_str}")

        # Format documents and facts for prompt
        formatted_documents = format_documents(documents)
        formatted_facts = format_facts()

        # Get the email composition prompt
        prompt = get_prompt(
            name="tool_write_email",
            label="latest"
        )

        # Format the system prompt
        system_prompt = prompt.compile(
            documents=formatted_documents,
            facts=formatted_facts
        )

        # Create generation trace
        generation = create_generation(
            trace=span,
            name="tool_write_email",
            model=prompt.config.get("model", "gpt-4"),
            input=system_prompt,
            metadata={"conversation_id": span.trace_id}
        )

        # Get completion from LLM
        completion_result = await completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": query}
            ],
            model=prompt.config.get("model", "gpt-4"),
            json_mode=True
        )

        # Parse response
        try:
            email_data = json.loads(completion_result)
            subject = email_data.get("subject", "Message from iAgent")
            body = email_data.get("body", "")
            scheduled_at = email_data.get("scheduled_at")  # ISO8601 timestamp
        except json.JSONDecodeError as e:
            end_generation(generation, output=None, level="ERROR")
            raise Exception(f"Failed to parse email content: {str(e)}")

        # End the generation trace
        end_generation(generation, output=email_data)

        # Send email using resend
        result = resend.Emails.send({
            "from": "iagent@pruszyn.ski",
            "to": "jakub.mikolaj.pruszynski@gmail.com",
            "subject": subject,
            "text": body,  # Using plain text instead of HTML
        })

        result_details = [
            "Email Send Results:",
            f"Subject: {subject}",
            f"Status: Success",
            f"Email ID: {result.id if hasattr(result, 'id') else 'Not available'}",
            f"Recipient: {params.get('to', 'jakub.mikolaj.pruszynski@gmail.com')}",
            f"Content: {body}",
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

