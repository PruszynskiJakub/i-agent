import os
from typing import Dict, Any

from todoist_api_python.api import TodoistAPI

from llm.tracing import create_event
from models.document import Document, DocumentType
from utils.document import create_document, create_error_document


async def _complete_tasks(params: Dict[str, Any], span) -> Document:
    """Complete one or more Todoist tasks"""
    try:
        todoist_client = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
        task_ids = params.get("ids", [])

        if not task_ids:
            create_event(span, "complete_todoist_tasks", input=params, output="No tasks provided")
            return create_document(
                text="No task IDs provided",
                metadata_override={
                    "conversation_uuid": params.get("conversation_uuid", ""),
                    "source": "todoist",
                    "description": "No tasks to complete",
                    "name": "CompleteTodoistTasksResult",
                    "content_type": "full",
                }
            )

        successful_tasks = []
        failed_tasks = []

        for task_id in task_ids:
            try:
                task = todoist_client.get_task(task_id)

                is_success = todoist_client.close_task(task_id)
                create_event(
                    span,
                    "complete_todoist_single_task",
                    input={"task_id": task_id},
                    output={"success": is_success}
                )

                if is_success:
                    successful_tasks.append({
                        "id": task_id,
                        "content": task.content,
                        "project_id": task.project_id
                    })
                else:
                    failed_tasks.append({
                        "id": task_id,
                        "error": "Failed to complete task"
                    })

            except Exception as e:
                failed_tasks.append({
                    "id": task_id,
                    "error": str(e)
                })

        # Format the results
        total = len(task_ids)
        successful = len(successful_tasks)
        failed = len(failed_tasks)

        result = (
            f"Complete Tasks Summary\n"
            f"---------------------\n"
            f"Total todo items processed: {total}\n"
            f"Successfully completed: {successful}\n"
            f"Failed completions: {failed}\n\n"
            f"Successfully Completed Todos\n"
            f"-------------------------\n"
            + (
                "\n".join(
                    f"Todo: {task['content']}\n"
                    f"ID: {task['id']}\n"
                    for task in successful_tasks
                ) if successful_tasks else "No tasks were successfully completed"
            )
            + "\n\nFailed Todos\n------------\n"
            + (
                "\n".join(
                    f"Todo ID: {task['id']}\n"
                    f"Error: {task['error']}\n"
                    for task in failed_tasks
                ) if failed_tasks else "No failed tasks"
            )
        )
        create_event(
            span,
            "complete_todoist_tasks",
            input=params,
            output={"status": "success", "successful": successful_tasks, "failed": failed_tasks}
        )

        return create_document(
            text=result,
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "description": f"Completed {successful} todos successfully, {failed} failed",
                "name": "CompleteTodoistTasksResult",
                "type": DocumentType.DOCUMENT,
                "content_type": "full"
            }
        )

    except Exception as error:
        create_event(span, "complete_todoist_tasks", level="ERROR", input=params, output={"error": str(error)})
        return create_error_document(
            error=error,
            error_context="Failed to complete tasks",
            conversation_uuid=params.get("conversation_uuid", ""),
        )
