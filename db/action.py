import json
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from db.models import ActionModel, DocumentModel, ActionDocumentModel
from tools.types import Action
from document.types import Document
from db.document import find_document_by_uuid


def find_actions_by_conversation(conversation_uuid: str) -> List[Action]:
    """
    Retrieve all actions for a given conversation
    
    Args:
        conversation_uuid: UUID of the conversation
            
    Returns:
        List of Action objects
    """
    query = ActionModel.select().where(
        ActionModel.conversation_uuid == conversation_uuid
    ).order_by(ActionModel.created_at)
    
    actions = []
    for action_model in query:
        # Get associated documents
        documents = []
        for action_doc in action_model.action_documents:
            if doc := find_document_by_uuid(UUID(action_doc.document.uuid)):
                documents.append(doc)
                
        actions.append(Action(
            uuid=UUID(action_model.uuid),
            name=action_model.name,
            tool_uuid=UUID(action_model.tool_uuid),
            payload=action_model.payload,
            status=action_model.status,
            conversation_uuid=action_model.conversation_uuid,
            documents=documents,
            step_description=action_model.step_description
        ))
    
    return actions


def create_action(
    conversation_uuid: str,
    name: str,
    tool_uuid: UUID,
    payload: Dict[str, Any],
    status: str,
    documents: Optional[List[Document]] = None,
    step_description: str = ""
) -> Action:
    """
    Create and save a new action
    
    Args:
        conversation_uuid: UUID of the conversation
        name: Name of the action
        tool_uuid: UUID of the tool that performed the action
        payload: Action payload
        result: Action result
        status: Action status
        documents: List of documents associated with the action
            
    Returns:
        Created Action object
    """
    action_uuid = uuid4()
    
    # Create action record
    action_model = ActionModel.create(
        uuid=str(action_uuid),
        name=name,
        tool_uuid=str(tool_uuid),
        payload=payload,
        status=status,
        conversation_uuid=conversation_uuid,
        step_description=step_description
    )

    # Create action object
    action = Action(
        uuid=action_uuid,
        name=name,
        tool_uuid=tool_uuid,
        conversation_uuid=conversation_uuid,
        payload=payload,
        status=status,
        documents=documents or [],
        step_description=step_description
    )

    # Save documents and create relations
    if action.documents:
        from db.document import save_document
        for document in action.documents:
            save_document(document)
            ActionDocumentModel.create(
                action=action_model,
                document=document.uuid
            )

    return action


