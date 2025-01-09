import json

from agent.state import AgentState, update_step_info
from llm import open_ai
from llm.format import format_messages
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation


async def agent_understand(state: AgentState, trace) -> AgentState:
    """
    Creates an understanding of the user's request based on the current state.
    Updates and returns AgentState with understanding details.
    """
    try:
        # Get the understanding prompt from repository
        prompt = get_prompt(
            name="agent_understand",
            label="latest"
        )

        # Format the system prompt with current state
        system_prompt = prompt.compile()

        # Create generation trace
        generation = create_generation(
            trace=trace,
            name="agent_understand",
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

        # Parse response into Understanding object
        try:
            response_data = json.loads(completion)
            # Update state with understanding data
            updated_state = update_step_info(state, {
                'understanding': response_data.get("understanding", ""),
                'constraints': response_data.get("constraints", []),
                'requirements': response_data.get("requirements", [])
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
        raise Exception(f"Error in agent understand: {str(e)}")
