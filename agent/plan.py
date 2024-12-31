import json

from agent.state import AgentState
from agent.tools import get_tools
from agent.types import Plan
from llm import open_ai
from llm_utils.format import format_actions, format_messages, format_tools
from llm_utils.prompts import get_prompt
from llm_utils.tracing import create_generation, end_generation


async def agent_plan(state: AgentState, trace) -> Plan:
    """
    Creates a plan based on the current state.
    Returns a Plan object with thinking, step, tool, parameters, and required information.
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
            model=prompt.config.get("model", "gpt-4"),
            input=system_prompt,
            metadata={"conversation_id": state.conversation_uuid}
        )

        # Get completion from LLM
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                *format_messages(state.messages)
            ],
            model=prompt.config.get("model", "gpt-4"),
            json_mode=True
        )

        # Parse response into Plan object
        try:
            response_data = json.loads(completion)
            plan = Plan(
                _thinking=response_data.get("thinking", ""),
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

        return plan

    except Exception as e:
        raise Exception(f"Error in agent plan: {str(e)}")
