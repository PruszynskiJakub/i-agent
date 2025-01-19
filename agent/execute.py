import uuid
from uuid import UUID

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
        tool_handler = tool_handlers.get(tool)
        params = {
            **state.step_info.tool_action_params,
            "conversation_uuid": state.conversation_uuid
        }
        documents = await tool_handler(state.step_info.tool_action, params, execution_span)
        
        action_dict = {
            'name': state.step_info.tool_action,
            'tool_uuid': UUID(state.step_info.tool_uuid),
            'payload': state.step_info.tool_action_params,
            'status': 'SUCCESS',
            'documents': documents,
            'step_description': state.step_info.overview
        }

        updated_state = add_taken_action(state, action_dict)

        end_span(
            execution_span,
            output=updated_state.taken_actions[-1],
            level="DEFAULT",
            status_message="Tool execution successful"
        )

        return updated_state

    except Exception as e:
        error_msg = f"Error executing tool '{state.step_info.tool}': {str(e)}"
        
        action_dict = {
            'name': state.step_info.tool_action,
            'tool_uuid': UUID(state.step_info.tool_uuid),
            'payload': state.step_info.tool_action_params,
            'status': 'ERROR',
            'documents': [],
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
