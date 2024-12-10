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
    function: Callable[[Dict[str, Any]], str]
    required_params: Dict[str, str]
    optional_params: Dict[str, str]

@dataclass
class Action:
    """An action performed by a tool"""
    uuid: UUID
    name: str
    tool_uuid: UUID
    payload: dict
    result: Any

@dataclass
class State:
    """The state of the agent"""
    tools: List[Tool]
    conversation_uuid: str
    actions: List[Action] = field(default_factory=list)
    messages: List[Dict[str, Any]] = field(default_factory=list)
    config: Dict[str, Any] = field(default_factory=lambda: {
        "current_step": 0,
        "max_steps": 5
    })

@dataclass
class Document:
    """A document that can be processed by the agent"""
    uuid: UUID
    conversation_uuid: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
