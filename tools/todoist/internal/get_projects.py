import os
from uuid import uuid4
from todoist_api_python.api import TodoistAPI
from llm.tracing import create_event
from models.document import Document, DocumentMetadata, DocumentType


async def get_projects(span) -> Document:
    """Get all Todoist projects and return as a Document"""
    try:
        todoist_client = TodoistAPI(os.getenv("TODOIST_API_TOKEN"))
        event = create_event(span, "fetch_projects", input="Fetching all Todoist projects")
        projects = todoist_client.get_projects()
        
        # Format projects into a readable string
        projects_text = "\n".join([
            f"- {project.name} (ID: {project.id})" 
            for project in projects
        ])
        
        doc = Document(
            uuid=uuid4(),
            conversation_uuid="",  # This should be passed in from the caller
            text=projects_text,
            metadata=DocumentMetadata(
                type=DocumentType.DOCUMENT,
                source="todoist",
                description=f"List of {len(projects)} Todoist projects",
                name="todoist_projects",
                content_type="list"
            )
        )
        
        create_event(span, "projects_formatted", output=projects_text)
        return doc
        
    except Exception as e:
        error_msg = f"Error retrieving projects: {str(e)}"
        create_event(span, "projects_error", level="ERROR", output=error_msg)
        
        # Return error as document
        return Document(
            uuid=uuid4(),
            conversation_uuid="",
            text=error_msg,
            metadata=DocumentMetadata(
                type=DocumentType.DOCUMENT,
                source="todoist",
                description="Error retrieving Todoist projects",
                name="todoist_projects_error",
                content_type="error"
            )
        )
