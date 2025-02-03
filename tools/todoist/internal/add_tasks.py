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

        # Format the results into sections
        sections = []

        # Section 1: General Info
        total = len(tasks)
        successful = len(successful_tasks)
        failed = len(failed_tasks)

        sections.append("Summary")
        sections.append("-" * 7)
        sections.append(f"Total tasks processed: {total}")
        sections.append(f"Successfully added: {successful}")
        sections.append(f"Failed: {failed}")
        sections.append("")

        # Section 2: Successful Tasks
        sections.append("Successfully Added Tasks")
        sections.append("-" * 22)
        if successful_tasks:
            for task in successful_tasks:
                sections.append(f"Task ID: {task['task_id']}")
                sections.append(f"Title: {task['content']}")
                if task['description']:
                    sections.append(f"Description: {task['description']}")
                if task['labels']:
                    sections.append(f"Labels: {', '.join(task['labels'])}")
                sections.append(f"Project: {task['project']['name']} (ID: {task['project']['id']})")
                if task['due']:
                    sections.append(f"Due: {task['due']}")
                sections.append("")
        else:
            sections.append("No tasks were successfully added")
            sections.append("")

        # Section 3: Failed Tasks
        sections.append("Failed Tasks")
        sections.append("-" * 11)
        if failed_tasks:
            for task in failed_tasks:
                sections.append(f"Title: {task['content']}")
                sections.append(f"Error: {task['error']}")
                sections.append("")
        else:
            sections.append("No failed tasks")
            sections.append("")

        document_text = "\n".join(sections)

        create_event(
            span,
            "add_todoist_tasks",
            input=params,
            output={"status": "success", "successful": successful, "failed": failed}
        )

        return create_document(
            text=document_text,
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
