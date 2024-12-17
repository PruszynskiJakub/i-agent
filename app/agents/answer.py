from state import StateHolder
from app.ai.llm import LLMProvider
from app.services.trace import TraceService
from app.repository.prompt import PromptRepository

class AgentAnswer:
    def __init__(self, llm: LLMProvider, trace_service: TraceService, prompt_repository: PromptRepository):
        self.llm = llm
        self.trace_service = trace_service
        self.prompt_repository = prompt_repository

    async def invoke(self, state: StateHolder, parent_trace) -> str:
        """
        Generate final answer based on conversation state and trace the generation.
        
        Args:
            state: Current state of the conversation
            parent_trace: Parent trace for tracking
            
        Returns:
            str: Final answer for the user
        """
        try:
            
            # Get all messages from state
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in state.messages
            ]
            
            # Fetch prompt from repository
            prompt = self.prompt_repository.get_prompt(
                name="agent_answer",
                prompt_type="text",
                label="latest"
            )
            system_prompt = prompt.compile()
            model = prompt.config.get("model", "gpt-4")
            
            # Create generation trace
            generation = self.trace_service.create_generation(
                trace=parent_trace,
                name="final_answer",
                model=model,
                input=messages,
                metadata={"conversation_id": state.conversation_uuid}
            )
            
            # Generate the final answer
            final_answer = await self.llm.completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    *messages
                ],
                model=model
            )
            
            
            self.trace_service.end_generation(generation, output=final_answer)
            
            return final_answer
            
        except Exception as e:
            raise Exception(f"Error generating final answer: {str(e)}")
