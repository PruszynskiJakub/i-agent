import json

from models.state import (
    AgentState,
    AgentPhase,
    Thoughts,
    ToolCandidate
)
from llm import open_ai
from llm.format import format_actions_history, format_messages, format_tools, format_documents
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from tools import get_tools
from utils.state import update_phase


async def agent_plan(state: AgentState, trace) -> AgentState:
    """
    Creates a plan based on the current state.
    Updates and returns AgentState with new interaction info.
    """
    try:
        # Update phase to PLAN
        state = update_phase(state, AgentPhase.PLAN)
        
        # Get the planning prompt from repository
        prompt = get_prompt(
            name="agent_plan",
            label="latest"
        )

        # Format the system prompt with current state
        system_prompt = prompt.compile(
            tools=format_tools(get_tools()),
            actions=format_actions_history(state.action_history),
            documents=format_documents(state.documents)
        )

        # Create generation trace
        generation = create_generation(
            trace=trace,
            name="agent_plan",
            model=prompt.config.get("model", "gpt-4o"),
            input=system_prompt,
            metadata={"conversation_id": state.conversation_uuid}
        )

        # Get completion from LLM
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                state.messages[-1]
            ],
            model=prompt.config.get("model", "gpt-4o"),
            json_mode=True
        )

        try:
            response_data = json.loads(completion)
            
            # Create thoughts from response
            tool_candidates = [
                ToolCandidate(
                    tool_name=t["tool"],
                    reason=t["reason"],
                    query=t["query"]
                ) for t in response_data.get("tool_candidates", [])
            ]
            
            thoughts = Thoughts(
                chain_of_thought=response_data.get("overview", ""),
                tool_candidates=tool_candidates
            )
            
            updated_state = state.copy(thoughts=thoughts)
        except json.JSONDecodeError as e:
            generation.end(
                output=None,
                level="ERROR",
                status_message=f"Failed to parse JSON response: {str(e)}"
            )
            raise Exception(f"Failed to parse JSON response: {str(e)}")

        # End the generation trace
        end_generation(generation, output=response_data)

        return updated_state

    except Exception as e:
        raise Exception(f"Error in agent plan: {str(e)}")
