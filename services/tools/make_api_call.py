import requests
import json
import os
from typing import Any, Dict, Optional
from services.tools.agent_tool import AgentTool

class MakeApiCallTool(AgentTool):
    """Tool for making HTTP API calls"""
    
    name = "make_api_call"
    description = "Makes an HTTP request to the specified URL with optional JSON payload. Supports environment variable placeholders in format [[ENV_VAR]]"
    required_params = {
        "url": "The URL to make the request to. Can contain placeholders like [[ENV_VAR]]",
        "method": "The HTTP method to use (GET, POST, etc.)"
    }
    optional_params = {
        "payload": "JSON payload to send with the request. Can contain placeholders like [[ENV_VAR]]"
    }

    def _replace_env_placeholders(self, text: str) -> str:
        """
        Replace placeholders with environment variables
        
        Args:
            text: Text containing placeholders in format [[ENV_VAR]]
            
        Returns:
            Text with placeholders replaced by environment variable values
        """
        if not text:
            return text
            
        import re
        pattern = r'\[\[([^\]]+)\]\]'
        
        def replace_match(match):
            env_var = match.group(1)
            value = os.getenv(env_var)
            if value is None:
                raise ValueError(f"Environment variable {env_var} not found")
            return value
            
        return re.sub(pattern, replace_match, text)

    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an HTTP request with the given parameters
        
        Args:
            params: Dictionary containing:
                - url: The target URL (can contain [[ENV_VAR]] placeholders)
                - method: HTTP method (GET, POST, etc.)
                - payload: Optional JSON payload (can contain [[ENV_VAR]] placeholders)
        
        Returns:
            Dictionary containing response data:
                - status_code: HTTP status code
                - content: Response content
        """
        url = self._replace_env_placeholders(params["url"])
        method = params["method"].upper()
        payload = params.get("payload")
        
        if payload:
            if isinstance(payload, str):
                # Replace placeholders in string payload before parsing JSON
                payload = self._replace_env_placeholders(payload)
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON payload")
            elif isinstance(payload, dict):
                # Replace placeholders in dict values
                payload = {
                    k: self._replace_env_placeholders(v) if isinstance(v, str) else v 
                    for k, v in payload.items()
                }

        response = requests.request(
            method=method,
            url=url,
            json=payload if payload else None
        )

        return {
            "status_code": response.status_code,
            "content": response.text
        } 