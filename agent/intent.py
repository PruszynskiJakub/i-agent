from models.state import AgentState
from utils.state import update_phase, AgentPhase


async def agent_intent(state: AgentState, trace) -> AgentState:
    return update_phase(state, AgentPhase.INTENT)
