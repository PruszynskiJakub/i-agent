import os
from typing import Dict, Any
from uuid import uuid4

import requests

from llm.tracing import create_event
from models.document import Document, DocumentType
from utils.document import create_document, create_error_document


async def _move_tasks(params: Dict[str, Any], span) -> Document:
    """Move Todoist tasks between projects and sections using sync API"""
    try:
        api_token = os.getenv("TODOIST_API_TOKEN")
        tasks = params.get("tasks", [])

        if not tasks:
            create_event(span, "move_todoist_tasks", input=params, output="No tasks provided")
            return create_document(
                text="No tasks provided to move",
                metadata_override={
                    "conversation_uuid": params.get("conversation_uuid", ""),
                    "source": "todoist",
                    "name": "MoveTasksResult",
                    "description": "No tasks to move",
                    "type": DocumentType.DOCUMENT
                }
            )

        successful_moves = []
        failed_moves = []
        commands = []

        # First prepare all commands
        for task in tasks:
            task_id = task.get("id")
            if not task_id:
                failed_moves.append({
                    "error": "Missing task ID",
                    "task": task
                })
                continue

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

            commands.append((command, task))

        # Execute all commands in a single API call if we have any
        if commands:
            try:
                response = requests.post(
                    url="https://api.todoist.com/sync/v9/sync",
                    headers={"Authorization": f"Bearer {api_token}"},
                    json={"commands": [cmd[0] for cmd in commands]}
                )
                
                if not response.ok:
                    raise Exception(f"API request failed: {response.status_code} {response.text}")
                    
                result = response.json()
                for command, task in commands:
                    sync_status = result.get("sync_status", {}).get(command["uuid"])
                    if sync_status == "ok":
                        create_event(
                            span,
                            "move_todoist_single_task",
                            input={"task_id": task["id"], "command": command},
                            output=result
                        )
                        successful_moves.append({
                            "id": task["id"],
                            "project_id": task.get("project_id", "Not specified"),
                            "section_id": task.get("section_id", "Not specified"),
                            "parent_id": task.get("parent_id", "Not specified")
                        })
                    else:
                        error = result["sync_status"][command["uuid"]]
                        create_event(
                            span,
                            "move_todoist_tasks",
                            input={"task_id": task["id"], "command": command},
                            output=result,
                            level="ERROR"
                        )
                        failed_moves.append({
                            "id": task["id"],
                            "error": f"Sync API error: {error}"
                        })
            except Exception as e:
                # If the batch request fails, mark all tasks as failed
                for command, task in commands:
                    failed_moves.append({
                        "id": task["id"],
                        "error": str(e)
                    })

        # Format the results
        total = len(tasks)
        successful = len(successful_moves)
        failed = len(failed_moves)

        result = (
            f"Move Summary\n"
            f"------------\n"
            f"Total tasks processed: {total}\n"
            f"Successfully moved: {successful}\n"
            f"Failed moves: {failed}\n\n"
            f"Successfully Moved Tasks\n"
            f"----------------------\n"
            + (
                "\n".join(
                    f"Task ID: {task['id']}\n"
                    + (f"Moved to project: {task['project_id']}\n" if task['project_id'] != "Not specified" else "")
                    + (f"Moved to section: {task['section_id']}\n" if task['section_id'] != "Not specified" else "")
                    + (f"New parent: {task['parent_id']}\n" if task['parent_id'] != "Not specified" else "")
                    for task in successful_moves
                ) if successful_moves else "No tasks were successfully moved"
            )
            + "\n\nFailed Moves\n-----------\n"
            + (
                "\n".join(
                    f"Task ID: {task['id']}\nError: {task['error']}\n"
                    for task in failed_moves
                ) if failed_moves else "No failed moves"
            )
        )

        return create_document(
            text=result,
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "name": "MoveTasksResult",
                "description": f"Moved {successful} tasks successfully, {failed} failed",
                "type": DocumentType.DOCUMENT
            }
        )

    except Exception as error:
        error_msg = f"Failed to move tasks: {str(error)}"
        create_event(span, "move_tasks_error", level="ERROR", output={"error": str(error)})

        return create_error_document(
            error=error,
            error_context=error_msg,
            conversation_uuid=params.get("conversation_uuid", "")
        )
