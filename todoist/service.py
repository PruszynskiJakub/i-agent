from tools.types import ActionResult

def execute_todoist(action: str, params: dict[str, any], span) -> ActionResult:
    if action == "get_projects":
        return ActionResult(
            success=True,
            result="Projects retrieval not yet implemented"
        )
    
    return ActionResult(
        success=False,
        result=f"Unknown action: {action}"
    )
