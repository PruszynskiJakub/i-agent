import os
from typing import List, Dict, Optional

from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()
openai_client = AsyncOpenAI(api_key=os.environ["OPENAI_API_KEY"])


async def completion(
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        json_mode: bool = False
) -> str:
    response = await openai_client.chat.completions.create(
        model=model or "gpt-4o-mini",
        messages=messages,
        response_format={"type": "json_object"} if json_mode else {"type": "text"}
    )
    return response.choices[0].message.content
