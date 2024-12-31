from agent.state import StateHolder
from ai.llm import LLMProvider
from llm_utils.prompts import get_prompt
from llm_utils.tracing import create_generation, end_generation
from services.trace import TraceService
from repository.prompt import PromptRepository

class AgentAnswer:
    def __init__(self, llm: LLMProvider):
        self.llm = llm

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
            prompt = get_prompt(
                name="agent_answer",
                label="latest"
            )
            system_prompt = prompt.compile()
            model = prompt.config.get("model", "gpt-4")
            
            # Create generation trace
            generation = create_generation(
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
            
            
            end_generation(generation, output=final_answer)
            state.add_message(content=final_answer, role="assistant")
            
            return final_answer
            
        except Exception as e:
            raise Exception(f"Error generating final answer: {str(e)}")
