from agent.state import AgentState
from agent.types import Plan
from llm.tracing import create_span, end_span
from tools.provider import tool_handlers


async def agent_execute(state: AgentState, plan: Plan, trace) -> AgentState:
    """
    Executes the given plan and updates the state accordingly.
    Creates a trace span for the execution process.
    """
    execution_span = create_span(
        trace=trace,
        name=f"execute_{plan.tool}",
        input={
            "tool": plan.tool,
            "step": plan.step
        },
        metadata={"conversation_id": state.conversation_uuid}
    )

    try:
        tool = plan.tool
        tool_handler = tool_handlers.get(tool)
        action_result = await tool_handler('add_transaction', {"user_query": state.messages[-1].content}, execution_span)

        print(f"Action result: {action_result}")

        end_span(
            execution_span,
            output=action_result,
            level="DEFAULT",
            status_message="Tool execution successful"
        )

        return state

    except Exception as e:
        error_msg = f"Error executing tool '{plan.tool}': {str(e)}"
        end_span(
            execution_span,
            output={"error": str(e)},
            level="ERROR",
            status_message=error_msg
        )
        raise Exception(error_msg)
