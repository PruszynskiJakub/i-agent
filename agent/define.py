import json

from agent.state import AgentState, update_interaction, update_phase, AgentPhase
from agent.tools import get_tool_action_instructions
from llm import open_ai
from llm.format import format_messages, format_actions_history, format_documents, \
    format_interaction
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation, create_span, end_span, create_event
from todoist import get_dynamic_context


async def agent_define(state: AgentState, trace) -> AgentState:
    """
    Creates a definition based on the current state and plan.
    Updates and returns AgentState with complete step_info including parameters.
    """
    # Create span for the define phase
    span = create_span(trace, "agent_define")

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
            documents=format_documents(state.documents),
            tool=format_interaction(state.interaction),
            instructions=get_tool_action_instructions(state.interaction.tool, state.interaction.tool_action),
            dynamic_context=dynamic_context,
            actions=format_actions_history(state.action_history),
            facts=format_facts()
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
                *format_messages(state.messages)
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

        end_span(span, output=updated_state)
        return updated_state

    except Exception as e:
        error_msg = f"Error in agent define: {str(e)}"
        end_span(span, level="ERROR", status_message=error_msg)
        raise Exception(error_msg)
