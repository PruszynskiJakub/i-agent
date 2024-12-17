
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for the state holder"""
    current_step: int = 0
    max_steps: int = 5