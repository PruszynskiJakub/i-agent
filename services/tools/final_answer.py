from typing import Dict

from services.openai_service import OpenAIService
from services.prompts.answer import answer_prompt
from services.tools.agent_tool import AgentTool


class FinalAnswerTool(AgentTool):
    name = "final_answer"
    description = "Use this tool to provide your final answer to the user"
    required_params = {
        "query": "The original user query",
    }
    optional_params = {
        "context": "The context to use for the answer"
    }

    def __init__(self, openai_service: OpenAIService):
        super().__init__()
        self.openai_service = openai_service

    async def execute(self, params: dict) -> dict[str, str]:
        # Validate required parameters
        if "query" not in params:
            raise ValueError("The 'query' parameter is required")

        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": answer_prompt(params.get("context", "No context provided"))
            },
            {
                "role": "user",
                "content": params["query"]
            }
        ]

        # Get response from OpenAI
        answer = await self.openai_service.completion(
            messages=messages,
        )

        return {
            "answer": answer
        }
