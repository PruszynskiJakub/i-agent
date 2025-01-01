from agent.state import AgentState, add_taken_action
from agent.types import Definition, Plan
from llm.tracing import create_span, end_span
from models.action import Action
from tools.provider import tool_handlers


async def agent_execute(state: AgentState, definition: Definition, trace) -> AgentState:
    """
    Executes the given plan and updates the state accordingly.
    Creates a trace span for the execution process.
    """
    execution_span = create_span(
        trace=trace,
        name=f"execute_{definition.tool}",
        input={
            "tool": definition.tool,
            "action": definition.action
        },
        metadata={"conversation_id": state.conversation_uuid}
    )

    try:
        tool = definition.tool
        tool_handler = tool_handlers.get(tool)
        action_result = await tool_handler(definition.action, definition.params, execution_span)

        print(f"Action result: {action_result}")

        action = Action(
            uuid=action_result.uuid,
            name=definition.action,
            tool_uuid=definition.tool_uuid,
            payload=definition.params,
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
