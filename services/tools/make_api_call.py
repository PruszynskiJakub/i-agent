import requests
import json
from typing import Any, Dict, Optional
from services.tools.agent_tool import AgentTool

class MakeApiCallTool(AgentTool):
    """Tool for making HTTP API calls"""
    
    name = "make_api_call"
    description = "Makes an HTTP request to the specified URL with optional JSON payload"
    required_params = {
        "url": "The URL to make the request to",
        "method": "The HTTP method to use (GET, POST, etc.)"
    }
    optional_params = {
        "payload": "JSON payload to send with the request"
    }

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an HTTP request with the given parameters
        
        Args:
            params: Dictionary containing:
                - url: The target URL
                - method: HTTP method (GET, POST, etc.)
                - payload: Optional JSON payload
        
        Returns:
            Dictionary containing response data:
                - status_code: HTTP status code
                - content: Response content
        """
        url = params["url"]
        method = params["method"].upper()
        payload = params.get("payload")
        
        if payload and not isinstance(payload, dict):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                raise ValueError("Invalid JSON payload")

        response = requests.request(
            method=method,
            url=url,
            json=payload if payload else None
        )

        return {
            "status_code": response.status_code,
            "content": response.text
        } 