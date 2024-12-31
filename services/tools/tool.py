from ast import Dict
from dataclasses import dataclass
from typing import Any, Protocol

from services.tools.ynab import YnabService


class ToolService(Protocol):
    def execute(self, action: str, params: Dict[str, Any], trace) -> Any: ...

