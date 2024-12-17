from app.model.plan import Plan
from app.ai.llm import LLMProvider
from app.repository.prompt import PromptRepository
from app.utils.utils import format_actions_for_prompt, format_messages_for_completion
from state import StateHolder
from app.services.trace import TraceService
import json

class AgentPlan:
    def __init__(self, llm: LLMProvider, prompt_repository: PromptRepository, trace_service: TraceService):
        self.llm = llm
        self.prompt_repository = prompt_repository
        self.trace_service = trace_service

    def invoke(self, state: StateHolder, trace: TraceService) -> Plan:
        """
        Creates a plan based on the current state.
        Returns a Plan object with thinking, step, tool, parameters, and required information.
        """
        try:
            # Get the planning prompt from repository
            prompt = self.prompt_repository.get_prompt(
                name="agent_plan",
                prompt_type="text",
                label="latest"
            )

            # Format the system prompt with current state
            system_prompt = prompt.compile(
                formatted_tools="",
                taken_actions=format_actions_for_prompt(state.taken_actions)
            )

            # Create generation trace
            generation = trace.create_generation(
                name="agent_plan",
                model=prompt.config.get("model", "gpt-4"),
                input=system_prompt,
                metadata={"conversation_id": state.conversation_uuid}
            )

            # Get completion from LLM
            completion = self.llm.complete(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *format_messages_for_completion(state.messages)
                ],
                model=prompt.config.get("model", "gpt-4"),
                response_format={"type": "json"}
            )

            # Parse response into Plan object
            try:
                response_data = json.loads(completion)
                plan = Plan(
                    _thinking=response_data.get("thinking", ""),
                    step=response_data.get("step", ""),
                    tool=response_data.get("tool", ""),
                    parameters=response_data.get("parameters", {}),
                    required_information=response_data.get("required_information", [])
                )
            except json.JSONDecodeError as e:
                generation.end(
                    output=None,
                    level="ERROR",
                    status_message=f"Failed to parse JSON response: {str(e)}"
                )
                raise Exception(f"Failed to parse JSON response: {str(e)}")

            # End the generation trace
            generation.end(output=response_data)
            
            return plan

        except Exception as e:
            raise Exception(f"Error in agent plan: {str(e)}")