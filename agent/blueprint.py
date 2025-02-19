import json
import uuid

from llm import open_ai
from llm.format import format_facts, format_tools, format_tasks, format_thoughts
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from agent.state import (
    AgentState,
    AgentPhase,
    Task
)
from tools import get_tools
from utils.state import update_tasks


async def agent_blueprint(state: AgentState, trace) -> AgentState:
    """
    Creates a plan based on the current state.
    Updates and returns AgentState with new interaction info.
    """
    try:
        # Update phase to PLAN
        state = state.update_phase(AgentPhase.BLUEPRINT)

        # Get the planning prompt from repository
        prompt = get_prompt(
            name="agent_blueprint",
            label="latest"
        )

        system_prompt = prompt.compile(
            facts=format_facts(),
            thoughts=format_thoughts(state.thoughts),
            tools=format_tools(get_tools()),
            tasks=format_tasks(state.tasks)
        )

        # Create generation trace
        generation = create_generation(
            trace=trace,
            name="agent_blueprint",
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
            response_data = json.loads(completion)
            tasks = []
            for task_data in response_data["result"]:
                # Check if task already exists by UUID
                existing_task = next(
                    (t for t in state.tasks if t.uuid == task_data.get("uuid")),
                    None
                )

                if existing_task:
                    # Merge new data with existing task, preserving actions
                    tasks.append(Task(
                        uuid=existing_task.uuid,
                        name=task_data["name"],
                        description=task_data["description"],
                        status=task_data["status"],
                        conversation_uuid=state.conversation_uuid,
                        actions=existing_task.actions
                    ))
                else:
                    # Create new task with empty actions
                    tasks.append(Task(
                        uuid=str(uuid.uuid4()),
                        name=task_data["name"],
                        description=task_data["description"],
                        status=task_data["status"],
                        conversation_uuid=state.conversation_uuid,
                        actions=[]
                    ))

            new_state = update_tasks(state, tasks)

            # Persist tasks to database
            from db.tasks import save_task
            for task in tasks:
                save_task(task)

        except json.JSONDecodeError as e:
            generation.end(
                output=None,
                level="ERROR",
                status_message=f"Failed to parse JSON response: {str(e)}"
            )
            raise Exception(f"Failed to parse JSON response: {str(e)}")

        # End the generation trace
        end_generation(generation, output=response_data)

        return new_state

    except Exception as e:
        raise Exception(f"Error in agent plan: {str(e)}")
