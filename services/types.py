from dataclasses import dataclass
from typing import List, Any, Optional
from uuid import UUID

@dataclass
class Tool:
    """A tool that can be used by the agent"""
    uuid: UUID
    name: str
    description: str
    instructions: str

@dataclass
class Action:
    """An action performed by a tool"""
    tool: Tool
    uuid: UUID
    result: Any
    payload: dict

@dataclass
class State:
    """The state of the agent"""
    tools: List[Tool]
    action: Optional[Action] = None
