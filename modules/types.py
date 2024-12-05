from dataclasses import dataclass, field
from typing import List, Any, Optional, Callable, Dict
from uuid import UUID

@dataclass
class Tool:
    """A tool that can be used by the agent"""
    uuid: UUID
    name: str
    description: str
    instructions: str
    function: Callable[..., Any]
    required_params: Dict[str, str]
    optional_params: Dict[str, str]

@dataclass
class Action:
    """An action performed by a tool"""
    tool_uuid: UUID
    uuid: UUID
    name: str
    result: Any
    payload: dict

@dataclass
class State:
    """The state of the agent"""
    tools: List[Tool]
    actions: List[Action] = field(default_factory=list)
