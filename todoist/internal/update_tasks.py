from typing import Dict, Any
from uuid import uuid4

from llm.tracing import create_event
from todoist import todoist_client
from document.types import Document
from document.utils import create_document


async def update_tasks(params: Dict[str, Any], span) -> Document:
    """Update existing Todoist tasks with new information"""
    try:
        tasks = params.get("tasks", [])
        create_event(span, "update_tasks_start", input={"task_count": len(tasks)})
        
        if not tasks:
            return create_document(
                content="No tasks provided for update",
                metadata={
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
            if "projectId" in task:
                update_args["project_id"] = task["projectId"]
            
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
        sections = []
        
        # Summary section
        total = len(tasks)
        successful = len(successful_updates)
        failed = len(failed_updates)
        
        sections.append("Update Summary")
        sections.append("-" * 14)
        sections.append(f"Total tasks processed: {total}")
        sections.append(f"Successfully updated: {successful}")
        sections.append(f"Failed updates: {failed}")
        sections.append("")
        
        # Successful updates section
        sections.append("Successfully Updated Tasks")
        sections.append("-" * 24)
        if successful_updates:
            for task in successful_updates:
                sections.append(f"Task ID: {task['id']}")
                sections.append(f"Content: {task['content']}")
                if task['description']:
                    sections.append(f"Description: {task['description']}")
                if task['labels']:
                    sections.append(f"Labels: {', '.join(task['labels'])}")
                if task['due']:
                    sections.append(f"Due: {task['due']}")
                sections.append("")
        else:
            sections.append("No tasks were successfully updated")
            sections.append("")
        
        # Failed updates section
        sections.append("Failed Updates")
        sections.append("-" * 13)
        if failed_updates:
            for task in failed_updates:
                sections.append(f"Task ID: {task['id']}")
                sections.append(f"Error: {task['error']}")
                sections.append("")
        else:
            sections.append("No failed updates")
            sections.append("")

        result = "\n".join(sections)
        create_event(span, "update_tasks_complete", 
                    output={"status": "success", "successful": successful, "failed": failed})
        
        return create_document(
            content=result,
            metadata={
                "uuid": uuid4(),
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "name": "todoist_tasks",
                "description": f"Updated {successful} tasks successfully, {failed} failed"
            }
        )

    except Exception as error:
        error_msg = f"Failed to update tasks: {str(error)}"
        create_event(span, "update_tasks_error", level="ERROR", output={"error": str(error)})
        
        return create_document(
            content=error_msg,
            metadata={
                "uuid": uuid4(),
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "name": "todoist_tasks", 
                "description": "Error updating tasks"
            }
        )
