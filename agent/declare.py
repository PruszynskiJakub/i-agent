import json

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from models.state import AgentState, AgentPhase
from utils.state import (
    update_phase,
    update_current_task, find_task, update_current_tool
)


async def agent_declare(state: AgentState, trace) -> AgentState:
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
            name="agent_select",
            label="latest"
        )

        # Format system prompt with current state
        system_prompt = prompt.compile(
            tools="",
            facts="",
            tasks=""
        )

        # Create generation trace
        generation = create_generation(
            trace=trace,
            name="agent_select",
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
            result = json.loads(completion)['result']
            new_state = update_current_task(
                state,
                find_task(state, result["task_uuid"], result["task_name"])
            )
            new_state = update_current_tool(new_state, result["tool_name"])

        except json.JSONDecodeError as e:
            generation.end(
                output=None,
                level="ERROR",
                status_message=f"Failed to parse JSON response: {str(e)}"
            )
            raise Exception(f"Failed to parse JSON response: {str(e)}")

        # End the generation trace
        end_generation(generation, output=result)

        return new_state

    except Exception as e:
        raise Exception(f"Error in agent decide: {str(e)}")
