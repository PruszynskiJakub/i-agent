from services.tools.base import BaseTool

class FinalAnswerTool(BaseTool):
    @property
    def name(self) -> str:
        return "final_answer"
    
    @property
    def description(self) -> str:
        return "Use this tool to provide your final answer to the user"
    
    async def run(self, input_data: dict) -> dict:
        return input_data
