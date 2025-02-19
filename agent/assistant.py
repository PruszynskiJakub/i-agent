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


async def agent_run(initial_state: AgentState) -> AgentState:
    state = initial_state
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

        while state.should_continue():
            log_info(f"📍 Step {state.current_step + 1}/{state.max_steps}")

            state = await agent_blueprint(state, trace)
            state = await agent_declare(state, trace)

            if state.current_tool and state.current_tool == 'final_answer':
                log_info("🎯 Reached final answer step")
                break

            if state.current_tool:
                log_info(f"🔧 Using tool: {state.current_tool}")
                log_info(f"📝 Step overview: {state.current_action.name}")

            state = await agent_define(state, trace)
            state = await agent_execute(state, trace)
            state = state.complete_thinking_step()

        state = await agent_answer(state, trace)

        log_info("✅ Agent run completed")
        log_info(f"📊 Stats: {state.current_step} steps, {len(state.tasks)} tasks")

        end_trace(trace, output=state)
    except Exception as e:
        error_msg = f"❌ Error during agent run: {str(e)}"
        log_error(error_msg)
        raise
    return state
