import json

from llm import open_ai
from llm.format import format_facts, format_tasks, format_tool
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation, create_span, end_span, create_event
from agent.state import AgentPhase, AgentState
from tools.todoist import get_dynamic_context


async def agent_define(state: AgentState, trace) -> AgentState:
    """
    Creates a definition based on the current state and plan.
    Updates and returns AgentState with complete step_info including parameters.
    """
    # Create span for the define phase
    span = create_span(trace, "agent_define", input=state)

    try:
        # Update phase to DEFINE
        state = state.update_phase(AgentPhase.DEFINE)
        # Set dynamic context based on tool
        dynamic_context = ""
        if state.current_tool == "todoist":
            dynamic_context = get_dynamic_context()
            create_event(span, "dynamic_context_todoist", output=dynamic_context)

        # Get the definition prompt from repository
        prompt = get_prompt(
            name="agent_define",
            label="latest"
        )

        # Format the system prompt with current state
        system_prompt = prompt.compile(
            task_name=state.current_task.name,
            action_name=state.current_action.name,
            selected_tool=f"{state.current_tool}\n{format_tool(state.current_tool)}",
            facts=format_facts(),
            tool_context=dynamic_context,
            tasks=format_tasks(state.tasks),
            action=state.current_action
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
            result = response_data.get("result", {})

            action_updates = {
                "tool_action": result['action'],
                "input_payload": result.get("payload", {})
            }

            updated_state = state.update_current_action(action_updates)

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
