import os
from uuid import uuid4

from models.document import Document, DocumentType
from utils.document import create_document, create_error_document
from todoist_api_python.api import TodoistAPI

async def _search_tasks(params: dict, span) -> Document:
    """
    Search tasks based on provided filters (project, label, section, or specific ids)
    Returns a Document containing the formatted task list with detailed information
    """
    try:
        todoist_client = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
        filter_query = params.get("filter", "")
        project_id = params.get("project_id")
        label = params.get("label")
        section_id = params.get("section_id")
        task_ids = params.get("ids", [])
        due_before = params.get("due_before")
        due_after = params.get("due_after")

        # Build filter query
        date_filters = []
        if due_after:
            date_filters.append(f"due after: {due_after}")
        if due_before:
            date_filters.append(f"due before: {due_before}")
        
        if date_filters:
            if filter_query:
                filter_query = f"({filter_query}) & {' & '.join(date_filters)}"
            else:
                filter_query = ' & '.join(date_filters)

        # Get tasks with filters
        tasks = todoist_client.get_tasks(
            filter=filter_query or None,
            project_id=project_id,
            label=label,
            section_id=section_id,
            ids=task_ids
        )

        # Format the results
        task_count = len(tasks)

        result = (
            f"Search Todos Result\n"
            f"-----------------\n"
            f"Total todos found: {task_count}\n\n"
            f"Todo items\n"
            f"-----\n"
            + (
                "\n".join(
                    f"Item: {task.content}\n"
                    f"ID: {task.id}\n"
                    + (f"Labels: {', '.join(task.labels)}\n" if task.labels else "")
                    + (f"Description: {task.description}\n" if task.description else "")
                    + (f"Due: {task.due.string}" + (f" ({task.due.datetime})\n" if task.due.datetime else "\n") if task.due else "")
                    for task in tasks
                ) if tasks else "No tasks found"
            )
        )

        description = "List of Todoist todos"
        if filter_query:
            description += f" matching filter '{filter_query}'"
        if project_id:
            description += f" from project {project_id}"
        if label:
            description += f" with label '{label}'"
        if section_id:
            description += f" in section {section_id}"
        if task_ids:
            description += f" matching IDs: {', '.join(task_ids)}"

        return create_document(
            text=result,
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "type": DocumentType.DOCUMENT,
                "source": "todoist",
                "name": "SearchTodoistTasksResult",
                "description": description
            }
        )

    except Exception as e:
        return create_error_document(
            error=e,
            error_context="Error searching Todoist tasks",
            conversation_uuid=params.get("conversation_uuid", ""),
        )
