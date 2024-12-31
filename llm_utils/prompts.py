from typing import Optional, Union, List, Dict

from langfuse.model import TextPromptClient

from llm_utils import langfuse_client


def get_prompt(
        name: str,
        version: Optional[int] = None,
        label: Optional[str] = None,
        fallback: Optional[Union[str, List[Dict[str, str]]]] = None,
        cache_ttl_seconds: int = 60
) -> TextPromptClient:
    try:
        return langfuse_client.get_prompt(
            name=name,
            type="text",
            version=version,
            label=label,
            fallback=fallback,
            cache_ttl_seconds=cache_ttl_seconds
        )
    except Exception as e:
        raise Exception(f"Failed to fetch prompt '{name}': {str(e)}")
