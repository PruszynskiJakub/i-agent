from modules.types import State

class AgentService:
    def __init__(self, state: State, planning_service, execution_service, db_service, answer_service):
        self.state = state
        self.planning_service = planning_service
        self.execution_service = execution_service
        self.db_service = db_service
        self.answer_service = answer_service

    async def run(self, parent_trace=None) -> str:
        self._store_message(self.state.messages[-1]['content'], "user")

        while self.state.config["current_step"] < self.state.config["max_steps"]:
            plan_result = await self.planning_service.create_plan(
                self.state, self.state.messages, parent_trace
            )
            
            if plan_result["tool"] == "final_answer":
                break
                
            await self.execution_service.execute_plan(plan_result, self.state, parent_trace)
            self.state.config["current_step"] += 1

        final_answer = await self.answer_service.create_final_answer(
            self.state, self.state.messages, parent_trace
        )

        self._store_message(final_answer, "assistant")
        return final_answer
    
    def _store_message(self, message: str, role: str):
        self.db_service.store_message(self.state.conversation_uuid, role, message)

