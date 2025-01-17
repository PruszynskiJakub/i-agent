from todoist.internal.add_todos import add_todos
from todoist.internal.get_projects import get_projects
from tools.types import ActionResult


async def execute_todoist(action: str, params: dict[str, any], span) -> ActionResult:
    if action == "get_projects":
        doc = await get_projects(span)
        return ActionResult(
            result=doc.text,
            documents=[doc]
        )
    elif action == "add_todos":
        doc = await add_todos(params, span)
        return ActionResult(
            result=doc.text,
            documents=[doc]
        )

    return ActionResult(
        result=f"Unknown action: {action}"
    )
