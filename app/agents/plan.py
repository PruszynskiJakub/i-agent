from state import StateHolder
from app.services.trace import TraceService

class Plan:
    def invoke(self, state: StateHolder, trace: TraceService) -> dict:
        """
        Creates a plan based on the current state.
        Returns a dict with at least a 'tool' key.
        """
        # Implement your planning logic here
        pass