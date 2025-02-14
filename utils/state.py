from typing import List, Dict, Any

from db.message import find_messages_by_conversation, save_message
from db.conversation import load_conversation_documents
from models.state import AgentState, AgentPhase, Thoughts
from models.document import Document
from utils.message import create_message


def create_or_restore_state(conversation_uuid: str) -> AgentState:
    return AgentState(
        conversation_uuid=conversation_uuid,
        messages=find_messages_by_conversation(conversation_uuid),
        tasks=[],
        message_documents=load_conversation_documents(conversation_uuid),
        current_step=0,
        max_steps=4,
        phase=AgentPhase.INTENT,
        current_task=None,
        current_action=None,
        thoughts=Thoughts(),
        dynamic_context=""
    )


def complete_interaction(state: AgentState) -> AgentState:
    """
    Increments current_step by 1 and clears interaction and dynamic_context.

    Args:
        state: Current agent state

    Returns:
        Updated AgentState with incremented current_step and cleared fields
    """
    return state.copy(
        current_step=state.current_step + 1,
        interaction=None,
        dynamic_context=""
    )


def add_message(state: AgentState, content, role) -> AgentState:
    message = create_message(state.conversation_uuid, content, role)
    save_message(message)
    return state.copy(messages=[*state.messages, message])


def record_action(state: AgentState, action_dict: Dict[str, Any]) -> AgentState:
    """
    Create an ActionRecord in the database and add it to the state's action_history

    Args:
        state: Current agent state
        action_dict: Dictionary containing action data

    Returns:
        Updated AgentState with new action record in action_history
    """
    from db.action import save_action_record

    action_record = save_action_record(
        conversation_uuid=state.conversation_uuid,
        name=action_dict['name'],
        tool=action_dict.get('tool', ''),
        tool_uuid=action_dict.get('tool_uuid'),
        input_payload=action_dict['payload'],
        status="",
        output_documents=action_dict.get('documents', []),
        step_description=action_dict.get('step_description', '')
    )

    return state.copy(action_history=state.action_history + [action_record])


def add_documents(state: AgentState, documents: List[Document]) -> AgentState:
    return state.copy(documents=[*state.conversation_documents, *documents])

def update_phase(state: AgentState, new_phase: AgentPhase) -> AgentState:
    """
    Update the phase of the AgentState

    Args:
        state: Current agent state
        new_phase: The new phase to set

    Returns:
        Updated AgentState with new phase
    """
    return state.copy(phase=new_phase)

def set_dynamic_context(state: AgentState, context: str) -> AgentState:
    """
    Set the dynamic context in the AgentState

    Args:
        state: Current agent state
        context: New dynamic context string

    Returns:
        Updated AgentState with updated dynamic_context
    """
    return state.copy(dynamic_context=context)

def should_interact(state: AgentState) -> bool:
    return state.current_step < state.max_steps

def update_interaction(state: AgentState, updates: Dict[str, Any]) -> AgentState:
    current_values = {
        'overview': state.interaction.overview,
        'tool': state.interaction.tool,
        'tool_uuid': state.interaction.tool_uuid,
        'tool_action': state.interaction.tool_action,
        'query': state.interaction.query,
        'payload': state.interaction.payload
    }
    current_values.update(updates)
    return state.copy(interaction=Interaction(**current_values))

def new_interaction(state: AgentState) -> AgentState:
    """
    Create a new empty Interaction object with PENDING status and update the state with it.

    Args:
        state: Current agent state

    Returns:
        Updated AgentState with new empty interaction
    """
    interaction = Interaction(
        overview="",
        tool="",
        tool_uuid=None,
        tool_action="",
        query="",
        payload={},
        status="PENDING"
    )
    return state.copy(interaction=interaction)
