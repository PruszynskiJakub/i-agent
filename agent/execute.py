import json

from models.state import AgentState
from utils.document import create_error_document
from llm.tracing import create_span, end_span
from logger.logger import log_info, log_error, log_tool_call
from tools.__init__ import tool_handlers
from utils.state import record_action


async def agent_execute(state: AgentState, trace) -> AgentState:
    """
    Executes the given plan and updates the state accordingly.
    Creates a trace span for the execution process.
    """
    execution_span = create_span(
        trace=trace,
        name=f"execute_{state.interaction.tool}",
        input={
            "tool": state.interaction.tool,
            "action": state.interaction.tool_action
        },
        metadata={"conversation_uuid": state.conversation_uuid}
    )

    try:
        tool = state.interaction.tool
        tool_action = state.interaction.tool_action
        params = {
            **state.interaction.payload,
            "conversation_uuid": state.conversation_uuid
        }
        log_info(f"🔧 Executing tool '{tool}' with action '{tool_action}'\nParameters: {json.dumps(params, indent=2)}")

        tool_handler = tool_handlers.get(tool)
        documents = await tool_handler(state.interaction.tool_action, params, execution_span)

        log_tool_call(
            f"{tool}.{tool_action}",
            params,
            {"document_count": len(documents)}
        )

        action_dict = {
            'name': state.interaction.tool_action,
            'tool': tool,
            'tool_uuid': state.interaction.tool_uuid,
            'payload': state.interaction.payload,
            # 'status': 'SUCCESS',
            'documents': documents,
            'step_description': state.interaction.overview
        }

        updated_state = record_action(state, action_dict)

        log_info(
            f"✅ Tool execution successful: {tool} - {state.interaction.tool_action}\nResult documents: {len(documents)} document(s)")
        # for idx, doc in enumerate(documents, 1):
        #     log_info(f"Document {idx}: {doc.type.value} - {len(doc.content)} chars")
        #
        end_span(
            execution_span,
            output=updated_state.action_history[-1],
            level="DEFAULT",
            status_message="Tool execution successful"
        )

        return updated_state

    except Exception as e:
        error_msg = f"Error executing tool '{state.interaction.tool}': {str(e)}"
        log_error(error_msg)

        error_doc = create_error_document(
            error=e,
            error_context=f"Executing tool '{state.interaction.tool}' with action '{state.interaction.tool_action}'",
            conversation_uuid=state.conversation_uuid
        )

        action_dict = {
            'name': state.interaction.tool_action,
            'tool': state.interaction.tool,
            'tool_uuid': state.interaction.tool_uuid,
            'payload': state.interaction.payload,
            # 'status': 'ERROR',
            'documents': [error_doc],
            'step_description': state.interaction.overview
        }

        updated_state = record_action(state, action_dict)

        end_span(
            execution_span,
            output=updated_state.action_history[-1],
            level="ERROR",
            status_message=error_msg
        )

        return updated_state
