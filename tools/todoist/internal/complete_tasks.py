import os
from typing import Dict, Any

from todoist_api_python.api import TodoistAPI

from llm.tracing import create_event
from models.document import Document, DocumentType
from utils.document import create_document, create_error_document


async def complete_tasks(params: Dict[str, Any], span) -> Document:
    """Complete one or more Todoist tasks"""
    try:
        todoist_client = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
        task_ids = params.get("task_ids", [])

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
        sections = []

        # Summary section
        total = len(task_ids)
        successful = len(successful_tasks)
        failed = len(failed_tasks)

        sections.append("Task Completion Summary")
        sections.append("-" * 21)
        sections.append(f"Total tasks processed: {total}")
        sections.append(f"Successfully completed: {successful}")
        sections.append(f"Failed: {failed}")
        sections.append("")

        # Successful completions
        sections.append("Successfully Completed Tasks")
        sections.append("-" * 26)
        if successful_tasks:
            for task in successful_tasks:
                sections.append(f"Task: {task['content']}")
                sections.append(f"ID: {task['id']}")
                sections.append("")
        else:
            sections.append("No tasks were successfully completed")
            sections.append("")

        # Failed completions
        sections.append("Failed Tasks")
        sections.append("-" * 11)
        if failed_tasks:
            for task in failed_tasks:
                sections.append(f"Task ID: {task['id']}")
                sections.append(f"Error: {task['error']}")
                sections.append("")
        else:
            sections.append("No failed tasks")
            sections.append("")

        document_text = "\n".join(sections)
        create_event(
            span,
            "complete_todoist_tasks",
            input=params,
            output={"status": "success", "successful": successful_tasks, "failed": failed_tasks}
        )

        return create_document(
            text=document_text,
            metadata_override={
                "conversation_uuid": params.get("conversation_uuid", ""),
                "source": "todoist",
                "description": f"Completed {successful} tasks successfully, {failed} failed",
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
