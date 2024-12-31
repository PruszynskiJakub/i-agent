from agent.state import StateHolder
from ai.llm import LLMProvider
from llm_utils.tracing import create_span, end_span
from model.plan import Plan
from repository.prompt import PromptRepository
from services.trace import TraceService


class AgentExecute:
    def __init__(self, llm: LLMProvider):
        self.llm = llm
    
    async def invoke(self, state: StateHolder, plan: Plan, trace) -> None:
        """
        Executes the given plan and updates the state accordingly.
        Creates a trace span for the execution process.
        """
        execution_span = create_span(
            trace=trace,
            name=f"execute_{plan.tool}",
            input={
                "tool": plan.tool,
                "parameters": plan.parameters,
                "step": plan.step
            },
            metadata={"conversation_id": state.conversation_uuid}
        )

        try:
            # TODO 
            # Execute the tool
            

            end_span(
                execution_span,
                output="",
                level="DEFAULT",
                status_message="Tool execution successful"
            )

        except Exception as e:
            error_msg = f"Error executing tool '{plan.tool}': {str(e)}"
            end_span(
                output={"error": str(e)},
                level="ERROR",
                status_message=error_msg
            )
            raise Exception(error_msg)