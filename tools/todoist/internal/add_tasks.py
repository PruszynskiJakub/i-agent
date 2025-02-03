import os
from typing import Dict, Any
from uuid import uuid4

from todoist_api_python.api import TodoistAPI

from llm.tracing import create_event
from models.document import Document, DocumentMetadata, DocumentType
from tools.todoist import get_default_project_id, get_project_name
from utils.document import create_document, create_error_document


async def add_tasks(params: Dict[str, Any], span) -> Document:
    """Add task items with optional metadata"""
    try:
        todoist_client = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
        tasks = params.get("tasks", [])

        if not tasks:
            create_event(span, "add_todoist_tasks", input=params, output="No tasks provided")
            return create_document(
                text="No tasks provided",
                metadata_override={
                    "uuid": uuid4(),
                    "conversation_uuid": params.get("conversation_uuid", ""),
                    "source": "todoist",
                    "name": "AddTodoistTaskResult",
                    "description": "No tasks to process",
                    "type": DocumentType.DOCUMENT,
                    "content_type": "full"
                }
            )

        successful_tasks = []
        failed_tasks = []

        for task in tasks:
            if not task.get("title"):
                continue

            task_args = _build_task_args(task)

            try:
                task = todoist_client.add_task(**task_args)
                create_event(span, "add_todoist_single_task", input=task_args, output={"task_id": task.id})

                successful_tasks.append({
                    "task_id": task.id,
                    "content": task.content,
                    "description": task.description,
                    "labels": task.labels if hasattr(task, 'labels') else [],
                    "project": {"name": get_project_name(task.project_id), "id": task.project_id},
                    "due": task.due.string if task.due else None
                })
            except Exception as e:
                failed_tasks.append({
                    "content": task.get("title", "Unknown"),
                    "error": str(e)
                })

        # Format the results
        total = len(tasks)
        successful = len(successful_tasks)
        failed = len(failed_tasks)

        result = (
            f"Add Tasks Summary\n"
            f"----------------\n"
            f"Total tasks processed: {total}\n"
            f"Successfully added: {successful}\n"
            f"Failed adds: {failed}\n\n"
            f"Successfully Added Tasks\n"
            f"----------------------\n"
            + (
                "\n".join(
                    f"Task ID: {task['task_id']}\n"
                    f"Title: {task['content']}\n"
                    + (f"Description: {task['description']}\n" if task['description'] else "")
                    + (f"Labels: {', '.join(task['labels'])}\n" if task['labels'] else "")
                    + f"Project: {task['project']['name']}\n"
                    + (f"Due: {task['due']}\n" if task['due'] else "")
                    for task in successful_tasks
                ) if successful_tasks else "No tasks were successfully added"
            )
            + "\n\nFailed Tasks\n------------\n"
            + (
                "\n".join(
                    f"Title: {task['content']}\n"
                    f"Error: {task['error']}\n"
                    for task in failed_tasks
                ) if failed_tasks else "No failed tasks"
            )
        )

        create_event(
            span,
            "add_todoist_tasks",
            input=params,
            output={"status": "success", "successful": successful_tasks, "failed": failed_tasks}
        )

        return create_document(
            text=result,
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "name": "AddTodoistTaskResult",
                "description": f"Added {successful} tasks successfully, {failed} failed",
                "type": DocumentType.DOCUMENT,
                "content_type": "full"
            }
        )

    except Exception as error:
        error_msg = f"Failed to process tasks: {str(error)}"
        create_event(span, "add_todoist_tasksr", level="ERROR", input=params, output={"error": str(error)})

        return create_error_document(
            error=error,
            error_context=error_msg,
            conversation_uuid=params.get("conversation_uuid", "unknown")
        )


def _build_task_args(task) -> Dict:
    task_args = {
        "content": task["title"],
        "project_id": task.get("projectId", get_default_project_id()),  # Default to Inbox if not specified
    }

    # Add optional parameters if present
    if task.get("description"):
        task_args["description"] = task["description"]
    if task.get("priority"):
        task_args["priority"] = max(1, min(4, task["priority"]))  # Clamp between 1-4
    if task.get("labels"):
        task_args["labels"] = task["labels"]  # Using label names instead of IDs

    # Handle due date options
    if task.get("dueString"):
        task_args["due_string"] = task["dueString"]
        if task.get("dueLang"):
            task_args["due_lang"] = task["dueLang"]
    elif task.get("dueDate"):
        task_args["due_date"] = task["dueDate"]

    # Handle duration if specified
    if task.get("duration") and task.get("durationUnit"):
        task_args["duration"] = task["duration"]
        task_args["duration_unit"] = task["durationUnit"]
