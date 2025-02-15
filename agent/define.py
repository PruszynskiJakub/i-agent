import json

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation, create_span, end_span, create_event
from tools.todoist import get_dynamic_context
from utils.state import AgentState, update_interaction, update_phase, AgentPhase


async def agent_define(state: AgentState, trace) -> AgentState:
    """
    Creates a definition based on the current state and plan.
    Updates and returns AgentState with complete step_info including parameters.
    """
    # Create span for the define phase
    span = create_span(trace, "agent_define", input=state.interaction)

    try:
        # Update phase to DEFINE
        state = update_phase(state, AgentPhase.DEFINE)
        # Set dynamic context based on tool
        dynamic_context = ""
        if state.interaction.tool == "todoist":
            dynamic_context = get_dynamic_context()
            create_event(span, "dynamic_context_todoist", output=dynamic_context)

        # Get the definition prompt from repository
        prompt = get_prompt(
            name="agent_define",
            label="latest"
        )

        # Format the system prompt with current state
        system_prompt = prompt.compile(
            task_name="",
            action_name="",
            selected_tool="",
            facts="",
            tool_context="",
            tasks="",
            action=""
        )

        # Create generation trace
        generation = create_generation(
            trace=span,
            name="agent_define",
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

        # Parse response into Definition object
        try:
            response_data = json.loads(completion)
            updated_state = update_interaction(state, {
                'payload': response_data.get("payload", {})
            })

        except (json.JSONDecodeError, ValueError) as e:
            generation.end(
                output=None,
                level="ERROR",
                status_message=f"Failed to process response: {str(e)}"
            )
            raise Exception(f"Failed to process response: {str(e)}")

        # End the generation trace
        end_generation(generation, output=response_data)

        end_span(span, output=response_data)
        return updated_state

    except Exception as e:
        error_msg = f"Error in agent define: {str(e)}"
        end_span(span, level="ERROR", status_message=error_msg)
        raise Exception(error_msg)
