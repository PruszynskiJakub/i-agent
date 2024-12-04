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
    
    def log_span(self, 
                 trace: Any,
                 name: str,
                 input_data: Dict[str, Any],
                 output_data: Dict[str, Any],
                 span_type: str = "llm",
                 model: Optional[str] = None) -> None:
        """
        Log a span within a trace
        
        Args:
            trace: Trace object
            name: Name of the span
            input_data: Input data for the span
            output_data: Output data from the span
            span_type: Type of span (default: "llm")
            model: Model name if applicable
        """
        span = trace.span(
            name=name,
            input=input_data,
            output=output_data,
            type=span_type
        )
        if model:
            span.update(model=model)
        span.end()
    
    def end_trace(self, trace: Any) -> None:
        """
        End a trace
        
        Args:
            trace: Trace object to end
        """
        trace.end()
