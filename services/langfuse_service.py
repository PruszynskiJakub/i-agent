from langfuse.client import Langfuse
from typing import Optional, Dict, Any

class LangFuseService:
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
    
    def create_trace(self, options: Dict[str, str]) -> Any:
        """
        Create a new trace for conversation tracking
        
        Args:
            options: Dictionary containing trace options with keys:
                - id: Trace identifier
                - userid: User identifier
                - sessionid: Session identifier
                - name: Name of the trace
            
        Returns:
            Trace object
        """
        return self.client.trace(**options)

    def end_trace(self) -> None:
        """
        End a trace
        """
        self.client.flush()
