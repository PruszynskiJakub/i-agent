import json

from agent.state import AgentState, update_interaction, update_phase, AgentPhase
from agent.tools import get_tool_by_name, get_tool_action_instructions
from llm import open_ai
from llm.format import format_messages, format_actions_history, format_documents, \
    format_interaction, format_tool_instructions
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from todoist import get_dynamic_context as get_todoist_context
from ynab import get_dynamic_context as get_ynab_context


async def agent_define(state: AgentState, trace) -> AgentState:
    """
    Creates a definition based on the current state and plan.
    Updates and returns AgentState with complete step_info including parameters.
    """
    try:
        # Update phase to DEFINE
        state = update_phase(state, AgentPhase.DEFINE)
        # Set dynamic context based on tool and action
        dynamic_context = ""
        if state.interaction.tool == "todoist":
            dynamic_context = get_todoist_context()
        elif state.interaction.tool == "ynab" and state.interaction.tool_action == "add_transaction":
            dynamic_context = await get_ynab_context(state.interaction.query, trace)

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
            actions=format_actions_history(state.action_history)
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

        return updated_state

    except Exception as e:
        raise Exception(f"Error in agent define: {str(e)}")
