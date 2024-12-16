import uuid
from typing import Dict, Any
from modules.logging_service import log_info, log_error, log_tool_call
from modules.types import Action, ActionResult

class ExecutionService:
    def __init__(self, tool_registry, db_service):
        self.tool_registry = tool_registry
        self.db_service = db_service

    async def execute_plan(self, plan: Dict[str, Any], state, parent_trace=None) -> None:
        tool_name = plan["tool"]
        parameters = plan["parameters"]
        action_uuid = str(uuid.uuid4())

        execution_event = parent_trace.span(
            name=f"tool_execution_{tool_name}",
            input={
                "tool": tool_name,
                "parameters": parameters,
                "step": plan["step"]
            },
            metadata={
                "conversation_id": state.conversation_uuid,
                "action_id": action_uuid
            }
        )

        try:
            handler = self.tool_registry.get_handler(tool_name)
            result = await handler(parameters, state)
            
            log_info(f"Executing {tool_name} with parameters: {parameters}", style="bold magenta")
            log_tool_call(tool_name, parameters, result)
            
            action = Action(
                uuid=uuid.UUID(action_uuid),
                name=plan['step'],
                tool_uuid=next((tool.uuid for tool in state.tools if tool.name == tool_name), None),
                payload=plan["parameters"],
                result=result.result,
                status=result.status,
                documents=result.documents
            )
            self.db_service.store_action(action)
            
            if not hasattr(state, 'actions'):
                state.actions = []
            
            state.actions.append(action)
            state.documents.extend(result.documents)

            execution_event.end(
                output=result,
                level="DEFAULT",
                status_message="Tool execution successful"
            )
            
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {str(e)}"
            execution_event.end(
                output={"error": str(e)},
                level="ERROR",
                status_message=error_msg
            )
            log_error(error_msg)
            raise Exception(error_msg)
