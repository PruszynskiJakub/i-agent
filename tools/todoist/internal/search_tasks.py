import os
from uuid import uuid4

from models.document import Document
from utils.document import create_document, create_error_document
from todoist_api_python.api import TodoistAPI

async def search_tasks(params: dict, span) -> Document:
    """
    Search tasks based on provided filters (project, label, section, or specific ids)
    Returns a Document containing the formatted task list with detailed information
    """
    try:
        todoist_client = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
        # Extract filter parameters and conversation_uuid
        filter_query = params.get("filter")
        project_id = params.get("project_id")
        label = params.get("label")
        section_id = params.get("section_id")
        task_ids = params.get("ids", [])
        conversation_uuid = params.get("conversation_uuid")

        if not conversation_uuid:
            raise ValueError("conversation_uuid is required")

        # Get tasks with filters
        tasks = todoist_client.get_tasks(
            filter=filter_query,
            project_id=project_id,
            label=label,
            section_id=section_id,
            ids=task_ids
        )

        # Format tasks into detailed text
        formatted_tasks = []
        for task in tasks:
            task_details = [
                f"Task: {task.content}",
                f"ID: {task.id}"
            ]
            
            if task.labels:
                task_details.append(f"Labels: {', '.join(task.labels)}")
            
            if task.description:
                task_details.append(f"Description: {task.description}")
            
            if task.due:
                due_str = f"Due: {task.due.string}"
                if task.due.datetime:
                    due_str += f" ({task.due.datetime})"
                task_details.append(due_str)
            
            formatted_tasks.append("\n".join(task_details) + "\n")

        task_count = len(formatted_tasks)
        summary = f"Successfully fetched {task_count} {'task' if task_count == 1 else 'tasks'}"
        content = f"{summary}\n\n" + ("\n".join(formatted_tasks) if formatted_tasks else "No tasks found")
        
        description = "List of Todoist tasks"
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
            text=content,
            metadata_override={
                "uuid": str(uuid4()),
                "conversation_uuid": conversation_uuid,
                "type": "document",
                "source": "todoist",
                "name": "task_search",
                "description": description
            }
        )

    except Exception as e:
        return create_error_document(
            error=e,
            error_context="Error searching Todoist tasks",
            conversation_uuid=params.get("conversation_uuid", ""),
        )
