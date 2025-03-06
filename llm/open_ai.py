import os
from typing import List, Dict, Optional

import openai
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


def embedding(text, model="text-embedding-3-large"):
    response = openai.Embedding.create(input=text, model=model)
    return response["data"][0]["embedding"]