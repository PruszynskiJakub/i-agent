from dataclasses import dataclass
from typing import List
from uuid import UUID

@dataclass
class Tool:
    """A tool that can be used by the agent"""
    uuid: UUID
    name: str
    description: str
    instructions: str

@dataclass
class State:
    """The state of the agent"""
    tools: List[Tool]
