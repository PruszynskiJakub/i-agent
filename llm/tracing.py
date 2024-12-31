from typing import Optional, List, Dict, Any

from llm import langfuse_client


def create_trace(
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
    return langfuse_client.trace(
        name=name,
        user_id=user_id,
        session_id=session_id,
        metadata=metadata,
        tags=tags,
        input=input,
        version=version
    )

def create_span(
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

def create_generation(
                      trace,
                      name: str,
                      model: str,
                      input: Any,
                      model_parameters: Optional[Dict[str, Any]] = None,
                      metadata: Optional[Dict[str, Any]] = None):
    """Create a generation to track AI models outputs

    Args:
        trace: Parent trace object
        name: Identifier of the generation
        model: Name of the models used
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

def create_event(
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

def end_span(
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

def end_generation(
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

def end_trace(
              trace,
              input: Optional[Any] = None,
              output: Optional[Any] = None,
              level: Optional[str] = None,
              status_message: Optional[str] = None):
    """End a trace with input/output data

    Args:
        trace: Trace object to end
        input: Optional input data to update
        output: Optional output data to update
        level: Final level of the trace
        status_message: Status message (e.g. error details)
    """
    if input is not None:
        trace.update(input=input)
    if output is not None:
        trace.update(output=output)
    if level is not None:
        trace.update(level=level)
    if status_message is not None:
        trace.update(status_message=status_message)

def flush():
    """Flush all pending traces to Langfuse"""
    langfuse_client.flush()

def shutdown():
    """Shutdown the trace service and flush pending traces"""
    langfuse_client.flush()
    langfuse_client.shutdown()