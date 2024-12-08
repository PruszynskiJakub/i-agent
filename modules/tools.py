from typing import Dict, Any

async def answer_tool(params: Dict[str, Any]) -> str:
    """Simple tool that returns the user query"""
    return f"Processing query: {params['user_query']}"
