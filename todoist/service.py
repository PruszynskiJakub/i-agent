from tools.types import ActionResult, ActionStatus
from todoist.internal.get_projects import get_projects

async def execute_todoist(action: str, params: dict[str, any], span) -> ActionResult:
    if action == "get_projects":
        result = await get_projects(span)
        return ActionResult(
            status=ActionStatus.SUCCESS,
            result=result
        )
    
    return ActionResult(
        status=ActionStatus.FAILURE,
        result=f"Unknown action: {action}"
    )
