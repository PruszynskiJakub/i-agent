from langfuse.client import Langfuse
from typing import Optional, Dict, Any, Union, List

class LangfuseService:
    def __init__(self, public_key: str, secret_key: str, host: Optional[str] = None):
        """
        Initialize LangFuse service
        
        Args:
            public_key: LangFuse public key
            secret_key: LangFuse secret key
            host: Optional host URL for LangFuse API
        """
        self.client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )
    
    def create_trace(self, options: Dict[str, str]):
        """
        Create a new trace for conversation tracking
        """
        return self.client.trace(
            name=options.get("name"),
            user_id=options.get("userid"),
            session_id=options.get("sessionid"),
            tags=options.get("tags", [])
        )

    def finalize_trace(self, trace, input=None, output=None):
        """
        End a trace and flush data
        
        Args:
            trace: The trace to finalize
            input: Optional input data (e.g., conversation history)
            output: Optional output data (e.g., AI response)
        """
        if input is not None:
            trace.update(input=input)
        if output is not None:
            trace.update(output=output)
        self.client.flush()

    def shutdown(self):
        """
        Shutdown LangFuse client
        """
        self.client.flush()
        self.client.shutdown()

    def get_prompt(
        self,
        name: str,
        prompt_type: str = "text",
        version: Optional[int] = None,
        label: Optional[str] = None,
        cache_ttl_seconds: int = 60,
        fallback: Optional[Union[str, List[Dict[str, str]]]] = None,
        max_retries: int = 2,
        fetch_timeout_seconds: int = 20
    ):
        """
        Fetch a prompt from Langfuse with caching support
        
        Args:
            name: Unique name of the prompt within the Langfuse project
            prompt_type: Type of prompt - either "text" or "chat"
            version: Optional specific version to fetch
            label: Optional label to fetch (e.g. "production", "staging", "latest")
            cache_ttl_seconds: How long to cache the prompt locally (default 60s)
            fallback: Optional fallback prompt if fetch fails
            max_retries: Number of retries for failed fetches (default 2)
            fetch_timeout_seconds: Timeout per API call in seconds (default 20)
            
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
                cache_ttl_seconds=cache_ttl_seconds,
                fallback=fallback,
                max_retries=max_retries,
                fetch_timeout_seconds=fetch_timeout_seconds
            )
        except Exception as e:
            if fallback is None:
                raise Exception(f"Failed to fetch prompt '{name}': {str(e)}")
            # If fallback provided, the SDK will return the fallback prompt automatically
            return None
