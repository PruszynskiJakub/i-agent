from agent.state import AgentState
from llm.tracing import create_span, end_span

async def agent_decide(state: AgentState, trace) -> AgentState:
    """
    Process the agent's decision after planning phase
    
    Args:
        state: Current agent state
        trace: Current trace context
        
    Returns:
        Updated AgentState
    """
    span = create_span(trace, "agent_decide", input=state.decision)
    
    # For now just pass through the state
    # Future: Add decision processing logic here
    
    end_span(span, output=state.decision)
    return state
