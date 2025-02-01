import json
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from db.document import find_document_by_uuid
from db.models import ActionRecordModel, ActionDocumentModel
from models.action import ActionRecord
from models.document import Document


def find_action_records_by_conversation(conversation_uuid: str) -> List[ActionRecord]:
    """
    Retrieve all actions for a given conversation
    
    Args:
        conversation_uuid: UUID of the conversation
            
    Returns:
        List of Action objects
    """
    query = ActionRecordModel.select().where(
        ActionRecordModel.conversation_uuid == conversation_uuid
    ).order_by(ActionRecordModel.created_at)
    
    records = []
    for record_model in query:
        # Get associated documents
        documents = []
        for action_doc in record_model.action_documents:
            if doc := find_document_by_uuid(UUID(action_doc.document.uuid)):
                documents.append(doc)
                
        records.append(ActionRecord(
            name=record_model.name,
            tool=record_model.tool,
            tool_uuid=UUID(record_model.tool_uuid) if record_model.tool_uuid else None,
            status=record_model.status,
            input_payload=record_model.payload,
            output_documents=documents,
            step_description=record_model.step_description
        ))
    
    return records


def save_action_record(
    conversation_uuid: str,
    name: str,
    tool: str,
    tool_uuid: Optional[UUID],
    input_payload: Dict[str, Any],
    status: str,
    output_documents: Optional[List[Document]] = None,
    step_description: str = ""
) -> ActionRecord:
    """
    Create and save a new action record
    
    Args:
        conversation_uuid: UUID of the conversation
        name: Name of the action
        tool: Name of the tool
        tool_uuid: UUID of the tool that performed the action
        input_payload: Action input payload
        status: Action status
        output_documents: List of output documents
        step_description: Description of the step
            
    Returns:
        Created ActionRecord object
    """
    record_uuid = uuid4()
    
    # Create action record in DB
    record_model = ActionRecordModel.create(
        uuid=str(record_uuid),
        name=name,
        tool=tool,
        tool_uuid=str(tool_uuid) if tool_uuid else None,
        payload=input_payload,
        status=status,
        conversation_uuid=conversation_uuid,
        step_description=step_description
    )

    # Create ActionRecord object
    record = ActionRecord(
        name=name,
        tool=tool,
        tool_uuid=tool_uuid,
        status=status,
        input_payload=input_payload,
        output_documents=output_documents or [],
        step_description=step_description
    )

    # Save documents and create relations
    if output_documents:
        from db.document import save_document
        for document in output_documents:
            save_document(document)
            ActionDocumentModel.create(
                action=record_model,
                document=document.uuid
            )

    return record


