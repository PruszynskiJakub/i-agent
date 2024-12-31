from ast import Dict
from typing import Any, Protocol


class ToolService(Protocol):
    def execute(self, action: str, params: Dict[str, Any], trace) -> Any: ...