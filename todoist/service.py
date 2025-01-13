from tools.types import ActionResult
from todoist.internal.get_projects import get_projects

async def execute_todoist(action: str, params: dict[str, any], span) -> ActionResult:
    if action == "get_projects":
        result = await get_projects(span)
        return ActionResult(
            success=True,
            result=result
        )
    
    return ActionResult(
        success=False,
        result=f"Unknown action: {action}"
    )
