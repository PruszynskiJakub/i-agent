import uuid

from agent.state import AgentState, add_taken_action
from llm.tracing import create_span, end_span
from models.action import Action
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
        metadata={"conversation_id": state.conversation_uuid}
    )

    try:
        tool = state.step_info.tool
        tool_handler = tool_handlers.get(tool)
        action_result = await tool_handler(state.step_info.tool_action, state.step_info.tool_action_params, execution_span)

        print(f"Action result: {action_result}")

        action = Action(
            uuid=uuid.uuid4(),
            name=state.step_info.tool_action,
            tool_uuid=uuid.uuid4(), # TODO FIX this param
            payload=state.step_info.tool_action_params,
            result=action_result.result,
            status=action_result.status,
            documents=action_result.documents
        )

        end_span(
            execution_span,
            output=action_result,
            level="DEFAULT",
            status_message="Tool execution successful"
        )

        return add_taken_action(state, action)

    except Exception as e:
        error_msg = f"Error executing tool '{definition.tool}': {str(e)}"
        end_span(
            execution_span,
            output={"error": str(e)},
            level="ERROR",
            status_message=error_msg
        )
        raise Exception(error_msg)
