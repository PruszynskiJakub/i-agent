from typing import Optional, Dict, Any, Union, List
from langfuse.client import Langfuse

class TraceService:
    def __init__(self, public_key: str, secret_key: str, host: str):
        """Initialize Trace service with Langfuse client
        
        Args:
            public_key: Langfuse public key
            secret_key: Langfuse secret key
            host: Optional host URL for Langfuse API
        """
        self.client = Langfuse(
            public_key=public_key,
            secret_key=secret_key,
            host=host
        )

    def create_trace(self, 
                    name: Optional[str] = None,
                    user_id: Optional[str] = None,
                    session_id: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None,
                    tags: Optional[List[str]] = None,
                    input: Optional[Any] = None,
                    version: Optional[str] = None):
        """Create a new trace for tracking an execution flow
        
        Args:
            name: Identifier of the trace
            user_id: ID of user that triggered execution
            session_id: Session identifier to group traces
            metadata: Additional metadata as JSON object
            tags: List of tags for categorizing traces
            input: Input data for the trace
            version: Version of the trace type
        """
        return self.client.trace(
            name=name,
            user_id=user_id,
            session_id=session_id,
            metadata=metadata,
            tags=tags,
            input=input,
            version=version
        )

    def create_span(self,
                   trace,
                   name: str,
                   input: Optional[Any] = None,
                   metadata: Optional[Dict[str, Any]] = None,
                   level: Optional[str] = None):
        """Create a span to track duration of work
        
        Args:
            trace: Parent trace object
            name: Identifier of the span
            input: Input data for the span
            metadata: Additional metadata
            level: Level (DEBUG, DEFAULT, WARNING, ERROR)
        """
        return trace.span(
            name=name,
            input=input,
            metadata=metadata,
            level=level
        )

    def create_generation(self,
                         trace,
                         name: str,
                         model: str,
                         input: Any,
                         model_parameters: Optional[Dict[str, Any]] = None,
                         metadata: Optional[Dict[str, Any]] = None):
        """Create a generation to track AI model outputs
        
        Args:
            trace: Parent trace object
            name: Identifier of the generation
            model: Name of the model used
            input: Prompt/input for generation
            model_parameters: Model configuration parameters
            metadata: Additional metadata
        """
        return trace.generation(
            name=name,
            model=model,
            input=input,
            model_parameters=model_parameters,
            metadata=metadata
        )

    def create_event(self,
                    trace,
                    name: str,
                    input: Optional[Any] = None,
                    output: Optional[Any] = None,
                    level: Optional[str] = None,
                    metadata: Optional[Dict[str, Any]] = None):
        """Create an event to track discrete events
        
        Args:
            trace: Parent trace object
            name: Identifier of the event
            input: Input data for the event
            output: Output data from the event
            level: Level (DEBUG, DEFAULT, WARNING, ERROR)
            metadata: Additional metadata
        """
        return trace.event(
            name=name,
            input=input,
            output=output,
            level=level,
            metadata=metadata
        )

    def end_span(self,
                span,
                output: Optional[Any] = None,
                level: Optional[str] = None,
                status_message: Optional[str] = None):
        """End a span with output data
        
        Args:
            span: Span object to end
            output: Output data from the span
            level: Final level of the span
            status_message: Status message (e.g. error details)
        """
        span.end(
            output=output,
            level=level,
            status_message=status_message
        )

    def end_generation(self,
                      generation,
                      output: Any,
                      usage: Optional[Dict[str, Any]] = None,
                      level: Optional[str] = None,
                      status_message: Optional[str] = None):
        """End a generation with output and usage data
        
        Args:
            generation: Generation object to end
            output: Generated output/completion
            usage: Token/resource usage statistics
            level: Final level of the generation
            status_message: Status message (e.g. error details)
        """
        generation.end(
            output=output,
            usage=usage,
            level=level,
            status_message=status_message
        )

    def flush(self):
        """Flush all pending traces to Langfuse"""
        self.client.flush()

    def shutdown(self):
        """Shutdown the trace service and flush pending traces"""
        self.client.flush()
        self.client.shutdown()
