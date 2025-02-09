from typing import List

from models.state import AgentState, Thoughts, ToolCandidate
from utils.state import update_phase, AgentPhase

async def agent_brainstorm(state: AgentState, trace) -> AgentState:
    """
    Brainstorm phase handler - generates initial tool ideas and reasoning
    before detailed planning.

    Args:
        state: Current agent state
        trace: Tracing context for logging/debugging

    Returns:
        Updated AgentState with brainstorming results and next phase
    """
    with create_span(trace, "brainstorm") as span:
        # Generate initial thoughts about approach and potential tools
        messages = [
            {"role": "system", "content": "You are an AI assistant helping to brainstorm approaches to solve a user's request."},
            {"role": "user", "content": f"""
Based on this user request, brainstorm potential approaches and relevant tools that could help solve it.
Focus on high-level strategy before detailed planning.

User Request: {state.user_query}

Available Tools:
{state.tools_str}

Respond with:
1. Initial thoughts on the overall approach
2. 2-3 potential tools that could be relevant and why
3. Any key considerations or constraints to keep in mind
"""}
        ]
        
        completion_response = await completion(messages)
        
        # Extract key insights from brainstorming
        thoughts = Thoughts(
            reasoning=completion_response,
            tool_candidates=[
                ToolCandidate(name=tool["name"], reasoning=tool["description"]) 
                for tool in state.tools[:3]  # Start with top 3 most relevant tools
            ]
        )
        
        # Update state with brainstorming results
        updated_state = state.copy(
            thoughts=thoughts
        )
        
        return update_phase(updated_state, AgentPhase.PLAN)
