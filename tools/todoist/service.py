from typing import List

from models.document import Document
from tools.todoist.internal.add_tasks import add_tasks
from tools.todoist.internal.complete_tasks import complete_tasks
from tools.todoist.internal.move_tasks import move_tasks
from tools.todoist.internal.search_tasks import search_tasks
from tools.todoist.internal.update_tasks import update_tasks
from utils.document import create_error_document


async def execute_todoist(action: str, params: dict[str, any], span) -> List[Document]:
    try:
        if action == "add_tasks":
            doc = await add_tasks(params, span)
            return [doc]
        elif action == "search_tasks":
            doc = await search_tasks(params, span)
            return [doc]
        elif action == "update_tasks":
            doc = await update_tasks(params, span)
            return [doc]
        elif action == "complete_tasks":
            doc = await complete_tasks(params, span)
            return [doc]
        elif action == "move_tasks":
            doc = await move_tasks(params, span)
            return [doc]
        else:
            return [
                create_error_document(
                    Exception(f"Unknown action: {action}"),
                    f"Todoist service received unknown action",
                    params.get("conversation_uuid", "")
                )
            ]
    except Exception as exception:
        return [
            create_error_document(
                exception,
                f"Error executing Todoist action: {action}",
                params.get("conversation_uuid", "")
            )
        ]
