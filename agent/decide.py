import json

from agent.state import (
    AgentState,
    AgentPhase,
    update_phase,
    update_interaction
)
from llm import open_ai
from llm.format import (
    format_actions_history,
    format_messages,
    format_tools,
    format_documents,
    format_tool_candidates, format_tools_with_instructions
)
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from agent.tools import get_tools_by_names


async def agent_decide(state: AgentState, trace) -> AgentState:
    """
    Process the agent's decision after planning phase
    
    Args:
        state: Current agent state
        trace: Current trace context
        
    Returns:
        Updated AgentState with decision
    """
    try:
        # Update phase to DEFINE
        state = update_phase(state, AgentPhase.DEFINE)
        
        # Get the decision prompt
        prompt = get_prompt(
            name="agent_decide",
            label="latest"
        )

        # Format system prompt with current state
        system_prompt = prompt.compile(
            tools=format_tools_with_instructions(get_tools_by_names([c.tool_name for c in state.thoughts.tool_candidates])) if state.thoughts else [],
            actions=format_actions_history(state.action_history),
            documents=format_documents(state.documents),
            tool_candidates=format_tool_candidates(state.thoughts.tool_candidates) if state.thoughts else "",
            overview=state.thoughts.chain_of_thought if state.thoughts else ""
        )

        # Create generation trace
        generation = create_generation(
            trace=trace,
            name="agent_decide",
            model=prompt.config.get("model", "gpt-4o"),
            input=system_prompt,
            metadata={"conversation_id": state.conversation_uuid}
        )

        # Get completion from LLM
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                *format_messages(state.messages)
            ],
            model=prompt.config.get("model", "gpt-4o"),
            json_mode=True
        )

        try:
            response_data = json.loads(completion)
            
            # Update interaction with chosen tool
            updated_state = update_interaction(state, {
                'overview': response_data.get("overview", ""),
                'tool': response_data.get("tool", ""),
                'tool_uuid': response_data.get("tool_uuid"),
                'tool_action': response_data.get("tool_action"),
                'query': response_data.get("query", ""),
                'payload': {}
            })

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
        raise Exception(f"Error in agent decide: {str(e)}")
