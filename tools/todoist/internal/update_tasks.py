import os
from typing import Dict, Any
from uuid import uuid4

from llm.tracing import create_event
from todoist_api_python.api import TodoistAPI

from models.document import Document, DocumentType
from utils.document import create_document


async def _update_tasks(params: Dict[str, Any], span) -> Document:
    """Update existing Todoist tasks with new information"""
    try:
        todoist_client = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
        tasks = params.get("tasks", [])
        create_event(span, "update_tasks_start", input={"task_count": len(tasks)})
        
        if not tasks:
            return create_document(
                text="No tasks provided for update",
                metadata_override={
                    "uuid": uuid4(),
                    "conversation_uuid": params.get("conversation_uuid", ""),
                    "source": "todoist",
                    "name": "todoist_tasks",
                    "description": "No tasks to update"
                }
            )

        successful_updates = []
        failed_updates = []

        for task in tasks:
            task_id = task.get("id")
            if not task_id:
                failed_updates.append({
                    "error": "Missing task ID",
                    "task": task
                })
                continue

            update_args = {
                'id': task_id
            }
            
            # Add optional update parameters if present
            if "content" in task:
                update_args["content"] = task["content"]
            if "description" in task:
                update_args["description"] = task["description"]
            if "priority" in task:
                update_args["priority"] = max(1, min(4, task["priority"]))
            if "labels" in task:
                update_args["labels"] = task["labels"]
            
            # Handle due date updates
            if "dueString" in task:
                update_args["due_string"] = task["dueString"]
                if "dueLang" in task:
                    update_args["due_lang"] = task["dueLang"]
            elif "dueDate" in task:
                update_args["due_date"] = task["dueDate"]
            
            # Handle duration updates
            if "duration" in task and "durationUnit" in task:
                update_args["duration"] = task["duration"]
                update_args["duration_unit"] = task["durationUnit"]

            try:
                updated_task = todoist_client.update_task(task_id=task_id, **update_args)
                create_event(span, "task_updated", input={"task_id": task_id, "updates": update_args})
                
                successful_updates.append({
                    "id": updated_task.id,
                    "content": updated_task.content,
                    "description": updated_task.description,
                    "labels": updated_task.labels if hasattr(updated_task, 'labels') else [],
                    "due": updated_task.due.string if updated_task.due else None
                })
            except Exception as e:
                failed_updates.append({
                    "id": task_id,
                    "error": str(e)
                })

        # Format the results
        total = len(tasks)
        successful = len(successful_updates)
        failed = len(failed_updates)

        result = (
            f"Update Tasks Summary\n"
            f"------------------\n"
            f"Total tasks processed: {total}\n"
            f"Successfully updated: {successful}\n"
            f"Failed updates: {failed}\n\n"
            f"Successfully Updated Tasks\n"
            f"----------------------\n"
            + (
                "\n".join(
                    f"Task ID: {task['id']}\n"
                    f"Content: {task['content']}\n"
                    + (f"Description: {task['description']}\n" if task['description'] else "")
                    + (f"Labels: {', '.join(task['labels'])}\n" if task['labels'] else "")
                    + (f"Due: {task['due']}\n" if task['due'] else "")
                    for task in successful_updates
                ) if successful_updates else "No tasks were successfully updated"
            )
            + "\n\nFailed Updates\n-------------\n"
            + (
                "\n".join(
                    f"Task ID: {task['id']}\n"
                    f"Error: {task['error']}\n"
                    for task in failed_updates
                ) if failed_updates else "No failed updates"
            )
        )
        create_event(span, "update_tasks_complete", 
                    output={"status": "success", "successful": successful, "failed": failed})
        
        return create_document(
            text=result,
            metadata_override={
                "uuid": uuid4(),
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "name": "todoist_tasks",
                "description": f"Updated {successful} tasks successfully, {failed} failed",
                "type": DocumentType.DOCUMENT
            }
        )

    except Exception as error:
        error_msg = f"Failed to update tasks: {str(error)}"
        create_event(span, "update_tasks_error", level="ERROR", output={"error": str(error)})
        
        return create_document(
            text=error_msg,
            metadata_override={
                "uuid": uuid4(),
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "name": "todoist_tasks", 
                "description": "Error updating tasks"
            }
        )
