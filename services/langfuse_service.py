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

    def finalize_trace(self, trace):
        """
        End a trace and flush data
        """
        self.client.flush()

    def shutdown(self):
        """
        Shutdown LangFuse client
        """
        self.client.flush()
        self.client.shutdown()
