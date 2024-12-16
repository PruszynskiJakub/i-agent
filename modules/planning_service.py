from typing import Dict, Any
import json
from modules.logging_service import log_info, log_error
from modules.utils import format_tools_for_prompt, format_actions_for_prompt

class PlanningService:
    def __init__(self, openai_service, langfuse_service):
        self.openai_service = openai_service
        self.langfuse_service = langfuse_service

    async def create_plan(self, state, messages, parent_trace=None) -> Dict[str, Any]:
        try:
            prompt = self.langfuse_service.get_prompt(
                name="agent_plan",
                prompt_type="text",
                label="latest"
            )
            
            system_prompt = prompt.compile(
                formatted_tools=format_tools_for_prompt(state.tools),
                taken_actions=format_actions_for_prompt(state.actions)
            )
            
            model = prompt.config.get("model", "gpt-4o-mini")
            
            generation = parent_trace.generation(
                name="agent_plan",
                model=model,
                input=system_prompt,
                metadata={"conversation_id": state.conversation_uuid}
            )
            
            completion = await self.openai_service.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                model=model,
                json_mode=True
            )
            
            try:
                response_data = json.loads(completion)
                log_info(f"Plan generated: {response_data}", style="bold blue")
            except json.JSONDecodeError as e:
                log_error(f"Failed to parse JSON response: {str(e)}")
                response_data = {}
            
            generation.end(output=response_data)
            return response_data
            
        except Exception as e:
            raise Exception(f"Error in planning service: {str(e)}")

    async def create_final_answer(self, state, messages, parent_trace=None) -> str:
        try:
            prompt = self.langfuse_service.get_prompt(
                name="agent_answer",
                prompt_type="text",
                label="latest"
            )
            
            system_prompt = prompt.compile()
            model = prompt.config.get("model", "gpt-4o-mini")
            
            generation = parent_trace.generation(
                name="agent_answer",
                model=model,
                input=system_prompt,
                metadata={"conversation_id": state.conversation_uuid}
            )
            
            final_answer = await self.openai_service.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                model=model
            )
            
            generation.end(output=final_answer)
            return final_answer
            
        except Exception as e:
            raise Exception(f"Error generating final answer: {str(e)}")
