import json
import uuid

from llm import open_ai
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from models.state import (
    AgentState,
    AgentPhase,
    Task
)
from utils.state import update_phase, update_tasks


async def agent_blueprint(state: AgentState, trace) -> AgentState:
    """
    Creates a plan based on the current state.
    Updates and returns AgentState with new interaction info.
    """
    try:
        # Update phase to PLAN
        state = update_phase(state, AgentPhase.PLAN)

        # Get the planning prompt from repository
        prompt = get_prompt(
            name="agent_blueprint",
            label="latest"
        )

        # TODO
        system_prompt = prompt.compile(
            facts="",
            thoughts="",
            tools="",
            tasks=""
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
            new_state = update_tasks(
                state,
                [
                    Task(
                        uuid=str(uuid.uuid4()),
                        name=task["name"],
                        description=task["description"],
                        status=task["status"],
                        actions=[]
                    )
                    for task in response_data["blueprint"]
                ]
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

        return new_state

    except Exception as e:
        raise Exception(f"Error in agent plan: {str(e)}")
