
from dataclasses import dataclass
from typing import List

from app.core.agent.tools.base import BaseTool


@dataclass
class AgentConfig:
    """Configuration for the state holder"""
    current_step: int = 0
    max_steps: int = 5
    tools: List[BaseTool] = []
