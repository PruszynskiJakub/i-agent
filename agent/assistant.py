import os

from agent.answer import agent_answer
from agent.blueprint import agent_blueprint
from agent.declare import agent_declare
from agent.define import agent_define
from agent.execute import agent_execute
from agent.intent import agent_intent
from llm.tracing import create_trace, end_trace
from logger.logger import log_info, log_error
from models.state import AgentState
from utils.state import should_continue, new_interaction, complete_interaction


async def agent_run(in_state: AgentState) -> str:
    state = in_state
    log_info(f"🚀 Starting agent run for query: {state.user_query[:200]}...")

    trace = create_trace(
        name=state.user_query[:45],  # First 45 chars of user input as trace name
        user_id=os.getenv("USER", "default_user"),
        metadata={
            'medium': 'slackk'
        },
        session_id=state.conversation_uuid,
        input=state.user_query
    )

    try:
        # Initial brainstorming phase
        log_info("🧠 Starting brainstorming phase...")
        state = await agent_intent(state, trace)

        while should_continue(state):
            log_info(f"📍 Step {state.current_step + 1}/{state.max_steps}")

            state = new_interaction(state)
            state = await agent_blueprint(state, trace)
            state = await agent_declare(state, trace)

            if state.interaction and state.interaction.tool == 'final_answer':
                log_info("🎯 Reached final answer step")
                break

            if state.interaction:
                log_info(f"🔧 Using tool: {state.interaction.tool}")
                log_info(f"📝 Step overview: {state.interaction.overview}")

            state = await agent_define(state, trace)
            state = await agent_execute(state, trace)
            state = complete_interaction(state)

        state = await agent_answer(state, trace)
        final_answer = state.assistant_response

        log_info("✅ Agent run completed")
        log_info(f"📊 Stats: {state.current_step} steps, {len(state.action_history)} actions")
        log_info(f"💡 Final answer: {final_answer[:200]}...")

        end_trace(trace, output=final_answer)
    except Exception as e:
        error_msg = f"❌ Error during agent run: {str(e)}"
        log_error(error_msg)
        raise
    return final_answer
