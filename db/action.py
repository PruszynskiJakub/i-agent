import json
from typing import List, Dict, Any, Optional
from uuid import UUID, uuid4

from db import execute
from tools.types import Action
from document.types import Document


def _row_to_action(row: tuple) -> Action:
    """Convert a database row to an Action object"""
    documents_json = json.loads(row[7])
    documents = [Document(**doc) for doc in documents_json] if documents_json else []
    
    return Action(
        uuid=UUID(row[0]),
        name=row[1],
        tool_uuid=UUID(row[2]),
        payload=json.loads(row[3]),
        result=row[4],
        status=row[5],
        conversation_uuid=row[6],
        documents=documents,
        step_description=row[8]
    )


def find_actions_by_conversation(conversation_uuid: str) -> List[Action]:
    """
    Retrieve all actions for a given conversation
    
    Args:
        conversation_uuid: UUID of the conversation
            
    Returns:
        List of Action objects
    """
    query = """
        SELECT uuid, name, tool_uuid, payload, result, status, conversation_uuid, documents, step_description
        FROM actions 
        WHERE conversation_uuid = ?
        ORDER BY created_at
    """
    rows = execute(query, (str(conversation_uuid),))
    return [_row_to_action(row) for row in rows]


def create_action(
    conversation_uuid: str,
    name: str,
    tool_uuid: UUID,
    payload: Dict[str, Any],
    result: str,
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
    action = Action(
        uuid=uuid4(),
        name=name,
        tool_uuid=tool_uuid,
        conversation_uuid=conversation_uuid,
        payload=payload,
        result=result,
        status=status,
        documents=documents or [],
        step_description=step_description
    )

    # Convert documents to JSON-serializable format
    documents_json = [doc.__dict__ for doc in action.documents]

    query = """
        INSERT INTO actions (
            uuid, name, tool_uuid, payload, result, status, 
            conversation_uuid, documents, step_description, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """
    execute(query, (
        str(action.uuid),
        action.name,
        str(action.tool_uuid),
        json.dumps(action.payload),
        action.result,
        action.status,
        conversation_uuid,
        json.dumps(documents_json),
        action.step_description
    ))

    return action


def ensure_action_table() -> None:
    """Ensure the actions table exists in the database"""
    query = """
        CREATE TABLE IF NOT EXISTS actions (
            uuid TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            tool_uuid TEXT NOT NULL,
            payload TEXT NOT NULL,
            result TEXT NOT NULL,
            status TEXT NOT NULL,
            conversation_uuid TEXT NOT NULL,
            documents TEXT NOT NULL,
            step_description TEXT NOT NULL DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    execute(query)


ensure_action_table()
