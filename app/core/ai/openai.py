from typing import Dict, List, Optional

from openai import AsyncOpenAI

from app.core.ai.llm import LLMProvider


class OpenAIProvider(LLMProvider):
    """OpenAI implementation of LLM provider"""
    
    def __init__(self, api_key: str):
        self.client = AsyncOpenAI(api_key=api_key)
        
    async def completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        json_mode: bool = False
    ) -> str:
        response = await self.client.chat.completions.create(
            model=model or "gpt-4-turbo-preview",
            messages=messages,
            response_format={"type": "json_object"} if json_mode else {"type": "text"}
        )
        return response.choices[0].message.content
