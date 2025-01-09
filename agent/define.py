import json

from agent.state import AgentState, update_step_info
from llm import open_ai
from llm.format import format_messages, format_tool_instructions
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from tools.provider import get_tool_by_name


async def agent_define(state: AgentState, trace) -> AgentState:
    """
    Creates a definition based on the current state and plan.
    Updates and returns AgentState with complete step_info including parameters.
    """
    try:
        # Get the definition prompt from repository
        prompt = get_prompt(
            name="agent_define",
            label="latest"
        )

        # Format the system prompt with current state
        system_prompt = prompt.compile(
            instructions=format_tool_instructions(get_tool_by_name(state.step_info.tool)),
            understanding=state.understanding
        )

        # Create generation trace
        generation = create_generation(
            trace=trace,
            name="agent_define",
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

        # Parse response into Definition object
        try:
            response_data = json.loads(completion)
            # Update state with response data
            updated_state = update_step_info(state, {
                'tool_action': response_data.get("action", state.step_info.tool_action),
                'tool_action_params': response_data.get("params", {})
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
        raise Exception(f"Error in agent define: {str(e)}")
