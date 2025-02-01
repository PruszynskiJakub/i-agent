import os
from typing import Dict, Any
from uuid import uuid4
import requests

from llm.tracing import create_event
from models.document import Document
from utils.document import create_document


async def move_tasks(params: Dict[str, Any], span) -> Document:
    """Move Todoist tasks between projects and sections using sync API"""
    try:
        api_token = os.getenv("TODOIST_API_TOKEN")
        tasks = params.get("tasks", [])
        create_event(span, "move_tasks_start", input={"task_count": len(tasks)})
        
        if not tasks:
            return create_document(
                content="No tasks provided to move",
                metadata={
                    "uuid": uuid4(),
                    "conversation_uuid": params.get("conversation_uuid", ""),
                    "source": "todoist",
                    "name": "todoist_tasks",
                    "description": "No tasks to move"
                }
            )

        successful_moves = []
        failed_moves = []

        for task in tasks:
            task_id = task.get("id")
            if not task_id:
                failed_moves.append({
                    "error": "Missing task ID",
                    "task": task
                })
                continue

            # Prepare move command
            command = {
                "type": "item_move",
                "uuid": uuid4().hex,
                "args": {
                    "id": task_id
                }
            }
            
            # Add optional move parameters if present
            if "project_id" in task:
                command["args"]["project_id"] = task["project_id"]
            if "section_id" in task:
                command["args"]["section_id"] = task["section_id"]
            if "parent_id" in task:
                command["args"]["parent_id"] = task["parent_id"]

            try:
                response = requests.post(
                    "https://api.todoist.com/sync/v9/sync",
                    headers={"Authorization": f"Bearer {api_token}"},
                    json={"commands": [command]}
                )
                response.raise_for_status()
                
                result = response.json()
                if result["sync_status"][command["uuid"]] == "ok":
                    create_event(span, "task_moved", input={"task_id": task_id, "command": command})
                    successful_moves.append({
                        "id": task_id,
                        "project_id": task.get("project_id", "Not specified"),
                        "section_id": task.get("section_id", "Not specified"),
                        "parent_id": task.get("parent_id", "Not specified")
                    })
                else:
                    error = result["sync_status"][command["uuid"]]
                    failed_moves.append({
                        "id": task_id,
                        "error": f"Sync API error: {error}"
                    })
            except Exception as e:
                failed_moves.append({
                    "id": task_id,
                    "error": str(e)
                })

        # Format the results
        sections = []
        
        # Summary section
        total = len(tasks)
        successful = len(successful_moves)
        failed = len(failed_moves)
        
        sections.append("Move Summary")
        sections.append("-" * 12)
        sections.append(f"Total tasks processed: {total}")
        sections.append(f"Successfully moved: {successful}")
        sections.append(f"Failed moves: {failed}")
        sections.append("")
        
        # Successful moves section
        sections.append("Successfully Moved Tasks")
        sections.append("-" * 22)
        if successful_moves:
            for task in successful_moves:
                sections.append(f"Task ID: {task['id']}")
                if task['project_id'] != "Not specified":
                    sections.append(f"Moved to project: {task['project_id']}")
                if task['section_id'] != "Not specified":
                    sections.append(f"Moved to section: {task['section_id']}")
                if task['parent_id'] != "Not specified":
                    sections.append(f"New parent: {task['parent_id']}")
                sections.append("")
        else:
            sections.append("No tasks were successfully moved")
            sections.append("")
        
        # Failed moves section
        sections.append("Failed Moves")
        sections.append("-" * 11)
        if failed_moves:
            for task in failed_moves:
                sections.append(f"Task ID: {task['id']}")
                sections.append(f"Error: {task['error']}")
                sections.append("")
        else:
            sections.append("No failed moves")
            sections.append("")

        result = "\n".join(sections)
        create_event(span, "move_tasks_complete", 
                    output={"status": "success", "successful": successful, "failed": failed})
        
        return create_document(
            content=result,
            metadata={
                "uuid": uuid4(),
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "name": "todoist_tasks",
                "description": f"Moved {successful} tasks successfully, {failed} failed"
            }
        )

    except Exception as error:
        error_msg = f"Failed to move tasks: {str(error)}"
        create_event(span, "move_tasks_error", level="ERROR", output={"error": str(error)})
        
        return create_document(
            content=error_msg,
            metadata={
                "uuid": uuid4(),
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "name": "todoist_tasks", 
                "description": "Error moving tasks"
            }
        )
