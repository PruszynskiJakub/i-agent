from todoist import todoist_client
from llm.tracing import create_generation, end_generation, create_event
from llm.open_ai import completion
from llm.prompts import get_prompt

async def get_projects(span) -> str:
    """Get all Todoist projects and format them nicely"""
    try:
        event = create_event(span, "fetch_projects", input="Fetching all Todoist projects")
        projects = todoist_client.get_projects()
        
        # Format projects into a readable string
        projects_text = "\n".join([
            f"- {project.name} (ID: {project.id})" 
            for project in projects
        ])
        
        result = f"Your Todoist projects:\n{projects_text}"
        create_event(span, "projects_formatted", output=result)
        return result
        
    except Exception as e:
        error_msg = f"Error retrieving projects: {str(e)}"
        create_event(span, "projects_error", level="ERROR", output=error_msg)
        return error_msg
