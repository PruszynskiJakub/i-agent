from typing import Optional, Union, List, Dict
from langfuse.client import Langfuse

class PromptRepository:
    def __init__(self, langfuse_client: Langfuse):
        """
        Initialize PromptRepository with a Langfuse client
        
        Args:
            langfuse_client: Initialized Langfuse client instance
        """
        self.client = langfuse_client

    def get_prompt(
        self,
        name: str,
        prompt_type: str = "text",
        version: Optional[int] = None,
        label: Optional[str] = None,
        fallback: Optional[Union[str, List[Dict[str, str]]]] = None,
        cache_ttl_seconds: int = 60
    ):
        """
        Fetch a prompt from Langfuse
        
        Args:
            name: Name of the prompt to fetch
            prompt_type: Either "text" or "chat"
            version: Optional specific version to fetch
            label: Optional label to fetch (e.g. "production", "staging")
            fallback: Optional fallback prompt if fetch fails
            cache_ttl_seconds: How long to cache the prompt locally
            
        Returns:
            Langfuse prompt object that can be used with .compile() method
            
        Raises:
            Exception if fetch fails and no fallback provided
        """
        try:
            return self.client.get_prompt(
                name=name,
                type=prompt_type,
                version=version,
                label=label,
                fallback=fallback,
                cache_ttl_seconds=cache_ttl_seconds
            )
        except Exception as e:
            if fallback is None:
                raise Exception(f"Failed to fetch prompt '{name}': {str(e)}")
            return None
