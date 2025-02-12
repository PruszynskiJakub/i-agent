import json

from models.state import AgentState, AgentPhase
from utils.state import (
    update_phase,
    update_interaction
)
from llm import open_ai
from llm.format import (
    format_actions_history,
    format_messages,
    format_documents,
    format_tool_candidates,
    format_tools_with_descriptions,
    format_facts
)
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from tools.__init__ import get_tools_by_names


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
        state = update_phase(state, AgentPhase.DECIDE)
        
        # Get the decision prompt
        prompt = get_prompt(
            name="agent_decide",
            label="latest"
        )

        # Format system prompt with current state
        system_prompt = prompt.compile(
            tools=format_tools_with_descriptions(get_tools_by_names([c.tool_name for c in state.thoughts.tool_thoughts])) if state.thoughts else [],
            actions=format_actions_history(state.action_history),
            documents=format_documents(state.conversation_documents),
            tool_candidates=format_tool_candidates(state.thoughts.tool_thoughts) if state.thoughts else "",
            overview=state.thoughts.chain_of_thought if state.thoughts else "",
            facts=format_facts()
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
                state.messages[-1]
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
