import json
import uuid

from llm import open_ai
from llm.format import format_facts, format_tools, format_tasks
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from models.state import AgentState, AgentPhase, TaskAction
from tools import get_tools
from utils.state import (
    update_current_task, find_task, update_current_action
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
        state = state.update_phase(AgentPhase.DECIDE)

        # Get the decision prompt
        prompt = get_prompt(
            name="agent_select",
            label="latest"
        )

        # Format system prompt with current state
        system_prompt = prompt.compile(
            tools=format_tools(get_tools()),
            facts=format_facts(),
            tasks=format_tasks(state.tasks)
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
            selected_task = find_task(state, result["task_uuid"])

            action = TaskAction(
                uuid=str(uuid.uuid4()),
                name=result["name"],
                task_uuid=selected_task.uuid,
                tool_uuid=result["tool_name"],
                status="pending",
                input_payload={},
                step=state.current_step,
                tool_action=""
            )
            new_state = update_current_task(
                state,
                selected_task
            )
            new_state = new_state.update_current_tool(result["tool_name"])
            new_state = update_current_action(new_state, action.model_dump())

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
