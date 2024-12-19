class AnswerService:
    def __init__(self, openai_service, langfuse_service):
        self.openai_service = openai_service
        self.langfuse_service = langfuse_service

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

