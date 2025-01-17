from typing import Dict, Any, List
from uuid import uuid4

from llm.tracing import create_event
from todoist import todoist_client
from document.types import Document, DocumentType, DocumentMetadata


async def add_todos(params: Dict[str, Any], span) -> Document:
    """Add todo items with optional metadata"""
    try:
        todos = params.get("todos", [])
        create_event(span, "add_todos_start", input={"todo_count": len(todos)})
        
        if not todos:
            return Document(
                uuid=uuid4(),
                conversation_uuid=params.get("conversation_uuid", ""),
                text="No todos provided",
                metadata=DocumentMetadata(
                    type=DocumentType.DOCUMENT,
                    source="todoist",
                    description="No todos to process",
                    name="todoist_todos",
                    content_type="error"
                )
            )

        successful_todos = []
        failed_todos = []

        for todo in todos:
            if not todo.get("title"):
                continue

            task_args = {
                "content": todo["title"],
                "project_id": todo.get("projectId", "2334150459"),  # Default to Inbox if not specified
            }

            # Add optional parameters if present
            if todo.get("description"):
                task_args["description"] = todo["description"]
            if todo.get("priority"):
                task_args["priority"] = max(1, min(4, todo["priority"]))  # Clamp between 1-4
            if todo.get("labels"):
                task_args["labels"] = todo["labels"]  # Using label names instead of IDs

            # Handle due date options
            if todo.get("dueString"):
                task_args["due_string"] = todo["dueString"]
                if todo.get("dueLang"):
                    task_args["due_lang"] = todo["dueLang"]
            elif todo.get("dueDate"):
                task_args["due_date"] = todo["dueDate"]

            # Handle duration if specified
            if todo.get("duration") and todo.get("durationUnit"):
                task_args["duration"] = todo["duration"]
                task_args["duration_unit"] = todo["durationUnit"]

            try:
                task = todoist_client.add_task(**task_args)
                create_event(span, "todo_added", input=task_args, output={"task_id": task.id})
                
                # Get project name for the task
                project_name = "Inbox"  # Default
                try:
                    if task.project_id:
                        project = todoist_client.get_project(task.project_id)
                        project_name = project.name
                except:
                    pass  # Keep default project name if lookup fails
                
                successful_todos.append({
                    "content": task.content,
                    "description": task.description,
                    "labels": task.labels if hasattr(task, 'labels') else [],
                    "project": {"name": project_name, "id": task.project_id},
                    "due": task.due.string if task.due else None
                })
            except Exception as e:
                failed_todos.append({
                    "content": todo.get("title", "Unknown"),
                    "error": str(e)
                })

        # Format the results into sections
        sections = []
        
        # Section 1: General Info
        total = len(todos)
        successful = len(successful_todos)
        failed = len(failed_todos)
        
        sections.append("Summary")
        sections.append("-" * 7)
        sections.append(f"Total todos processed: {total}")
        sections.append(f"Successfully added: {successful}")
        sections.append(f"Failed: {failed}")
        sections.append("")
        
        # Section 2: Successful Todos
        sections.append("Successfully Added Todos")
        sections.append("-" * 22)
        if successful_todos:
            for todo in successful_todos:
                sections.append(f"Title: {todo['content']}")
                if todo['description']:
                    sections.append(f"Description: {todo['description']}")
                if todo['labels']:
                    sections.append(f"Labels: {', '.join(todo['labels'])}")
                sections.append(f"Project: {todo['project']['name']} (ID: {todo['project']['id']})")
                if todo['due']:
                    sections.append(f"Due: {todo['due']}")
                sections.append("")
        else:
            sections.append("No todos were successfully added")
            sections.append("")
        
        # Section 3: Failed Todos
        sections.append("Failed Todos")
        sections.append("-" * 11)
        if failed_todos:
            for todo in failed_todos:
                sections.append(f"Title: {todo['content']}")
                sections.append(f"Error: {todo['error']}")
                sections.append("")
        else:
            sections.append("No failed todos")
            sections.append("")

        result = "\n".join(sections)
        create_event(span, "add_todos_complete", output={"status": "success", "successful": successful, "failed": failed})
        
        return Document(
            uuid=uuid4(),
            conversation_uuid=params.get("conversation_uuid", ""),
            text=result,
            metadata=DocumentMetadata(
                type=DocumentType.DOCUMENT,
                source="todoist",
                description=f"Added {successful} todos successfully, {failed} failed",
                name="todoist_todos",
                content_type="report"
            )
        )

    except Exception as error:
        error_msg = f"Failed to process todos: {str(error)}"
        create_event(span, "add_todos_error", level="ERROR", output={"error": str(error)})
        
        return Document(
            uuid=uuid4(),
            conversation_uuid=params.get("conversation_uuid", ""),
            text=error_msg,
            metadata=DocumentMetadata(
                type=DocumentType.DOCUMENT,
                source="todoist",
                description="Error processing todos",
                name="todoist_todos",
                content_type="error"
            )
        )
