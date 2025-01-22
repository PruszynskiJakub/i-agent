import uuid
import json
from uuid import UUID

from document.utils import create_error_document
from logger.logger import log_info, log_error, log_tool_call
from agent.state import AgentState, add_taken_action
from llm.tracing import create_span, end_span
from tools.types import Action
from tools.provider import tool_handlers


async def agent_execute(state: AgentState, trace) -> AgentState:
    """
    Executes the given plan and updates the state accordingly.
    Creates a trace span for the execution process.
    """
    execution_span = create_span(
        trace=trace,
        name=f"execute_{state.step_info.tool}",
        input={
            "tool": state.step_info.tool,
            "action": state.step_info.tool_action
        },
        metadata={"conversation_uuid": state.conversation_uuid}
    )

    try:
        tool = state.step_info.tool
        tool_action = state.step_info.tool_action
        params = {
            **state.step_info.tool_action_params,
            "conversation_uuid": state.conversation_uuid
        }
        log_info(f"🔧 Executing tool '{tool}' with action '{tool_action}'\nParameters: {json.dumps(params, indent=2)}")
        
        tool_handler = tool_handlers.get(tool)
        params = {
            **state.step_info.tool_action_params,
            "conversation_uuid": state.conversation_uuid
        }
        documents = await tool_handler(state.step_info.tool_action, params, execution_span)
        
        log_tool_call(
            f"{tool}.{tool_action}",
            params,
            {"document_count": len(documents)}
        )
        
        action_dict = {
            'name': state.step_info.tool_action,
            'tool_uuid': UUID(state.step_info.tool_uuid),
            'payload': state.step_info.tool_action_params,
            'status': 'SUCCESS',
            'documents': documents,
            'step_description': state.step_info.overview
        }

        updated_state = add_taken_action(state, action_dict)
        
        log_info(f"✅ Tool execution successful: {tool} - {state.step_info.tool_action}\nResult documents: {len(documents)} document(s)")
        for idx, doc in enumerate(documents, 1):
            log_info(f"Document {idx}: {doc.type.value} - {len(doc.content)} chars")
        
        end_span(
            execution_span,
            output=updated_state.taken_actions[-1],
            level="DEFAULT",
            status_message="Tool execution successful"
        )

        return updated_state

    except Exception as e:
        error_msg = f"Error executing tool '{state.step_info.tool}': {str(e)}"
        log_error(error_msg)
        
        error_doc = create_error_document(
            error=e,
            error_context=f"Executing tool '{state.step_info.tool}' with action '{state.step_info.tool_action}'",
            conversation_uuid=state.conversation_uuid
        )
        
        action_dict = {
            'name': state.step_info.tool_action,
            'tool_uuid': UUID(state.step_info.tool_uuid),
            'payload': state.step_info.tool_action_params,
            'status': 'ERROR',
            'documents': [error_doc],
            'step_description': state.step_info.overview
        }
        
        updated_state = add_taken_action(state, action_dict)
        
        end_span(
            execution_span,
            output=updated_state.taken_actions[-1],
            level="ERROR",
            status_message=error_msg
        )
        
        return updated_state
