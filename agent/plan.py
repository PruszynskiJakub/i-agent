import json

from agent.state import AgentState, update_step_info
from agent.types import Plan
from llm import open_ai
from llm.format import format_actions, format_messages, format_tools
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from tools.provider import get_tools


async def agent_plan(state: AgentState, trace) -> AgentState:
    """
    Creates a plan based on the current state.
    Updates and returns AgentState with new step_info.
    """
    try:
        # Get the planning prompt from repository
        prompt = get_prompt(
            name="agent_plan",
            label="latest"
        )

        # Format the system prompt with current state
        system_prompt = prompt.compile(
            formatted_tools=format_tools(get_tools()),
            taken_actions=format_actions(state.taken_actions)
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
                *format_messages(state.messages)
            ],
            model=prompt.config.get("model", "gpt-4o"),
            json_mode=True
        )

        # Parse response into Plan object
        try:
            response_data = json.loads(completion)
            plan = Plan(
                _thinking=response_data.get("_thinking", ""),
                step=response_data.get("step", ""),
                tool=response_data.get("tool", ""),
                tool_uuid=response_data.get("tool_uuid", ""),
            )
        except json.JSONDecodeError as e:
            generation.end(
                output=None,
                level="ERROR",
                status_message=f"Failed to parse JSON response: {str(e)}"
            )
            raise Exception(f"Failed to parse JSON response: {str(e)}")

        # End the generation trace
        end_generation(generation, output=response_data)

        # Update state with new step info
        updated_state = update_step_info(state, {
            'overview': plan._thinking,
            'tool': plan.tool,
            'tool_uuid': plan.tool_uuid,
            'tool_action': plan.step,
            'tool_action_params': {}
        })
        
        return updated_state

    except Exception as e:
        raise Exception(f"Error in agent plan: {str(e)}")
