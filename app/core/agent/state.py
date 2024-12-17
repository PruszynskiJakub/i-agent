from dataclasses import dataclass, field
from typing import Any, List, Dict
from uuid import UUID

from app.core.agent.config import AgentConfig

class StateHolder:
    """
    Holds the state of an agent conversation, including messages, actions, and documents.
    This class implements proper encapsulation and immutability where appropriate.
    
    Attributes:
        conversation_uuid (str): Unique identifier for the conversation
    """
    def __init__(self, conversation_uuid: str, config: AgentConfig = None) -> None:
        """
        Initialize a new StateHolder instance.
        
        Args:
            conversation_uuid: Unique identifier for the conversation
            config: Configuration for the state holder. If None, default config will be used.
        """
        self._conversation_uuid: str = conversation_uuid
        self._messages: List[Any] = []
        self._taken_actions: List[Any] = []
        self._documents: List[Any] = []
        self._config: AgentConfig = config if config is not None else AgentConfig()

    @property
    def conversation_uuid(self) -> str:
        """The unique identifier for this conversation."""
        return self._conversation_uuid

    @property
    def messages(self) -> List[Any]:
        """Get a copy of all messages in the conversation."""
        return self._messages.copy()

    def add_message(self, message: Any) -> None:
        """
        Add a new message to the conversation.
        
        Args:
            message: The message to add
        """
        self._messages.append(message)

    @property
    def taken_actions(self) -> List[Any]:
        """Get a copy of all actions taken in the conversation."""
        return self._taken_actions.copy()

    def add_action(self, action: Any) -> None:
        """
        Add a new action to the conversation.
        
        Args:
            action: The action to add
        """
        self._taken_actions.append(action)

    @property
    def documents(self) -> List[Any]:
        """Get a copy of all documents in the conversation."""
        return self._documents.copy()

    def add_document(self, document: Any) -> None:
        """
        Add a new document to the conversation.
        
        Args:
            document: The document to add
        """
        self._documents.append(document)

    @property
    def config(self) -> AgentConfig:
        """Get the current configuration."""
        return self._config

    def increment_step(self) -> None:
        """Increment the current step number."""
        self._config.current_step += 1

    def reset(self) -> None:
        """Reset the state to initial values."""
        self._messages.clear()
        self._taken_actions.clear()
        self._documents.clear()
        self._config = AgentConfig() 