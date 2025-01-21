from typing import List

from document.types import Document
from document.utils import create_error_document
from todoist.internal.add_tasks import add_tasks
from todoist.internal.get_projects import get_projects
from todoist.internal.search_tasks import search_tasks


async def execute_todoist(action: str, params: dict[str, any], span) -> List[Document]:
    try:
        if action == "get_projects":
            doc = await get_projects(span)
            return [doc]
        elif action == "add_tasks":
            doc = await add_tasks(params, span)
            return [doc]
        elif action == "search_tasks":
            doc = await search_tasks(params, span)
            return [doc]
        else:
            return [create_error_document(
                Exception(f"Unknown action: {action}"),
                f"Todoist service received unknown action",
                params.get("conversation_uuid", "")
            )]
    except Exception as e:
        return [create_error_document(
            e,
            f"Error executing Todoist action: {action}",
            params.get("conversation_uuid", "")
        )]
