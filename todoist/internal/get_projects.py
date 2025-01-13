from todoist import todoist_client
from llm.tracing import create_generation, end_generation
from llm.open_ai import completion
from llm.prompts import get_prompt

async def get_projects(span) -> str:
    """Get all Todoist projects and format them nicely"""
    try:
        projects = todoist_client.get_projects()
        
        # Format projects into a readable string
        projects_text = "\n".join([
            f"- {project.name} (ID: {project.id})" 
            for project in projects
        ])
        
        return f"Your Todoist projects:\n{projects_text}"
        
    except Exception as e:
        return f"Error retrieving projects: {str(e)}"
