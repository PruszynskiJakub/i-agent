import json

from agent.state import AgentState, Thoughts, AgentPhase
from llm import open_ai
from llm.format import format_facts, format_tools
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation
from models.state import ToolThought
from tools import get_tools


async def agent_intent(state: AgentState, trace) -> AgentState:
    """
      Creates a plan based on the current state.
      Updates and returns AgentState with new interaction info.
      """
    try:
        # Update phase to PLAN
        state = state.update_phase(AgentPhase.INTENT)

        # Get the planning prompt from repository
        prompt = get_prompt(
            name="agent_intent",
            label="latest"
        )

        # Format the system prompt with current state
        system_prompt = prompt.compile(
            tools=format_tools(get_tools()),
            facts=format_facts(),
        )

        # Create generation trace
        generation = create_generation(
            trace=trace,
            name="agent_intent",
            model=prompt.config.get("model", "gpt-4o"),
            input=system_prompt,
            metadata={"conversation_id": state.conversation_uuid}
        )

        # Get completion from LLM
        completion = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                *[
                    {"role": msg.role, "content": msg.content}
                    for msg in state.messages
                ]
            ],
            model=prompt.config.get("model", "gpt-4o"),
            json_mode=True
        )

        try:
            response_data = json.loads(completion)
            state = state.update_thoughts(
                Thoughts(
                    tool_thoughts=[
                        ToolThought(
                            query=tool_query["query"],
                            tool_name=tool_query["tool"]
                        ) for tool_query in response_data.get("queries", [])
                    ],
                    user_intent=response_data.get("intent", "I could not understand the user's intents.")
                )
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

        return state

    except Exception as e:
        raise Exception(f"Error in agent plan: {str(e)}")
