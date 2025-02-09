from models.state import AgentState
from utils.state import update_phase, AgentPhase


async def agent_brainstorm(state: AgentState, trace) -> AgentState:
    return update_phase(state, AgentPhase.BRAINSTORM)
