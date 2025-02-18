import json
from datetime import datetime

from llm.tracing import create_span, end_span
from logger.logger import log_info, log_error, log_tool_call
from models.state import AgentState
from tools.__init__ import tool_handlers
from utils.document import create_error_document
from utils.state import update_current_action


async def agent_execute(state: AgentState, trace) -> AgentState:
    """
    Executes the given plan and updates the state accordingly.
    Creates a trace span for the execution process.
    """
    execution_span = create_span(
        trace=trace,
        name=f"execute_{state.current_tool}",
        input={
            "tool": state.current_tool,
            "action": state.current_action.tool_action
        },
        metadata={"conversation_uuid": state.conversation_uuid}
    )

    try:
        tool = state.current_tool
        tool_action = state.current_action.tool_action
        params = {
            **state.current_action.input_payload,
            "conversation_uuid": state.conversation_uuid,
            "now": datetime.now().isoformat(),
        }
        log_info(f"🔧 Executing tool '{tool}' with action '{tool_action}'\nParameters: {json.dumps(params, indent=2)}")

        tool_handler = tool_handlers.get(tool)
        documents = await tool_handler(state.current_action.tool_action, params, execution_span)

        log_tool_call(
            f"{tool}.{tool_action}",
            params,
            {"document_count": len(documents)}
        )

        action_dict = {
            'status': 'completed',
            'output_documents': documents,
        }

        updated_state = update_current_action(state, action_dict)

        log_info(
            f"✅ Tool execution successful: {tool} - {state.current_action}\nResult documents: {len(documents)} document(s)")
        # for idx, doc in enumerate(documents, 1):
        #     log_info(f"Document {idx}: {doc.type.value} - {len(doc.content)} chars")

        end_span(
            execution_span,
            output=updated_state.current_action,
            level="DEFAULT",
            status_message="Tool execution successful"
        )

        return updated_state

    except Exception as e:
        error_msg = f"Error executing tool '{state.current_tool}': {str(e)}"
        log_error(error_msg)

        error_doc = create_error_document(
            error=e,
            error_context=f"Executing tool '{state.current_tool}' with action '{state.current_action}'",
            conversation_uuid=state.conversation_uuid
        )

        action_dict = {
            'status': 'completed',
            'documents': [error_doc],
        }

        updated_state = update_current_action(state, action_dict)

        end_span(
            execution_span,
            output=updated_state.current_action,
            level="ERROR",
            status_message=error_msg
        )

        return updated_state
