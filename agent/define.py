import json

from todoist import get_dynamic_context
from agent.state import AgentState, update_interaction, update_phase, AgentPhase
from llm import open_ai
from llm.format import format_messages, format_tool_instructions, format_actions_history, format_documents, \
    format_interaction
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from agent.tools import get_tool_by_name


async def agent_define(state: AgentState, trace) -> AgentState:
    """
    Creates a definition based on the current state and plan.
    Updates and returns AgentState with complete step_info including parameters.
    """
    try:
        # Update phase to DEFINE
        state = update_phase(state, AgentPhase.DEFINE)
        # Set dynamic context based on tool
        dynamic_context = ""
        if state.interaction.tool == "todoist":
            dynamic_context = get_dynamic_context()

        # Get the definition prompt from repository
        prompt = get_prompt(
            name="agent_define",
            label="latest"
        )

        # Format the system prompt with current state
        system_prompt = prompt.compile(
            documents=format_documents(state.documents),
            tool=format_interaction(state.interaction),
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
            
            # Validate response structure
            if "_reasoning" not in response_data:
                raise ValueError("Response missing required '_reasoning' field")
                
            # Update state with response data
            update_data = {
                'dynamic_context': response_data.get("_reasoning", ""),
                'payload': response_data.get("payload", {})
            }
            
            # If payload is null, mark interaction as failed
            if response_data.get("payload") is None:
                update_data['status'] = "ERROR"
                
            updated_state = update_interaction(state, update_data)
            
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
