from agent.state import AgentState, add_message
from llm import open_ai
from llm.format import format_actions
from llm.prompts import get_prompt
from llm.tracing import create_generation, end_generation


async def agent_answer(state: AgentState, parent_trace) -> AgentState:
    """
    Generate final answer based on conversation state and trace the generation.

    Args:
        state: Current state of the conversation
        parent_trace: Parent trace for tracking

    Returns:
        str: Final answer for the user
    """
    try:

        # Get all messages from state
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in state.messages
        ]

        # Fetch prompt from repository
        prompt = get_prompt(
            name="agent_answer",
            label="latest"
        )
        system_prompt = prompt.compile(
            taken_actions=format_actions(state.taken_actions),
            understanding=state.understanding,
            documents=state.documents
        )
        model = prompt.config.get("model", "gpt-4o")

        # Create generation trace
        generation = create_generation(
            trace=parent_trace,
            name="final_answer",
            model=model,
            input=system_prompt,
            metadata={"conversation_id": state.conversation_uuid}
        )

        # Generate the final answer
        final_answer = await open_ai.completion(
            messages=[
                {"role": "system", "content": system_prompt},
                *messages
            ],
            model=model
        )

        end_generation(generation, output=final_answer)
        
        return add_message(state, content=final_answer, role="assistant")

    except Exception as e:
        raise Exception(f"Error generating final answer: {str(e)}")
