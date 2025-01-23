import os

from logger.logger import log_info, log_error
from agent.answer import agent_answer
from agent.define import agent_define
from agent.execute import agent_execute
from agent.plan import agent_plan
from agent.state import AgentState, should_interact, complete_iteration
from llm.tracing import create_trace, end_trace


async def agent_run(in_state: AgentState) -> str:
    state = in_state
    user_query = state.messages[-1].content
    
    log_info(f"🚀 Starting agent run for query: {user_query[:200]}...")
    
    trace = create_trace(
        name=in_state.messages[-1].content[:45],  # First 45 chars of user input as trace name
        user_id=os.getenv("USER", "default_user"),
        metadata={
            'medium': 'slackk'
        },
        session_id=state.conversation_uuid,
        input=state.messages[-1].content,
    )

    try:
        while should_interact(state):
            log_info(f"📍 Step {state.current_step + 1}/{state.max_steps}")
            state = await agent_plan(state, trace)

            if state.step_info.tool == 'final_answer':
                log_info("🎯 Reached final answer step")
                break

            log_info(f"🔧 Using tool: {state.interaction.tool}")
            log_info(f"📝 Step overview: {state.interaction.overview}")
            
            state = await agent_define(state, trace)
            state = await agent_execute(state, trace)
            state = complete_iteration(state)

        state = await agent_answer(state, trace)
        final_answer = state.messages[-1].content
        
        log_info("✅ Agent run completed")
        log_info(f"📊 Stats: {state.current_step} steps, {len(state.taken_actions)} actions")
        log_info(f"💡 Final answer: {final_answer[:200]}...")

        end_trace(trace, output=final_answer)
    except Exception as e:
        error_msg = f"❌ Error during agent run: {str(e)}"
        log_error(error_msg)
        raise
    return final_answer
