from tools.types import ActionResult, ActionStatus
from todoist.internal.get_projects import get_projects
from todoist.internal.add_todos import add_todos

async def execute_todoist(action: str, params: dict[str, any], span) -> ActionResult:
    if action == "get_projects":
        result = await get_projects(span)
        return ActionResult(
            status=ActionStatus.SUCCESS,
            result=result
        )
    elif action == "add_todos":
        result = await add_todos(params, span)
        return ActionResult(
            status=ActionStatus.SUCCESS,
            result=result
        )
    
    return ActionResult(
        status=ActionStatus.FAILURE,
        result=f"Unknown action: {action}"
    )
