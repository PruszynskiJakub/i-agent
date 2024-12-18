
from dataclasses import dataclass, field
from typing import List

from tool.base import Tool


@dataclass
class AgentConfig:
    """Configuration for the state holder"""
    current_step: int = 0
    max_steps: int = 5
    tools: List[Tool] = field(default_factory=list)