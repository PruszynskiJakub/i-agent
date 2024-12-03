import base64
from services.tools.agent_tool import AgentTool


class Base64Tool(AgentTool):
    name = "base64"
    description = "Encode or decode content using Base64"
    required_params = {
        "content": "The content to encode/decode",
        "mode": "Either 'encode' or 'decode'"
    }
    optional_params = {}

    def execute(self, params: dict) -> dict:
        if "content" not in params:
            raise ValueError("The 'content' parameter is required")
        if "mode" not in params:
            raise ValueError("The 'mode' parameter is required")
        
        mode = params["mode"].lower()
        if mode not in ["encode", "decode"]:
            raise ValueError("Mode must be either 'encode' or 'decode'")

        content = params["content"]
        
        try:
            if mode == "encode":
                # Convert string to bytes and encode to base64
                result = base64.b64encode(content.encode()).decode()
            else:  # decode
                # Decode base64 string
                result = base64.b64decode(content.encode()).decode()
                
            return {"result": result}
        except Exception as e:
            return {"error": f"Base64 {mode} failed: {str(e)}"}
