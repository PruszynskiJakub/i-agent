from typing import List, Literal

from config import AgentConfig
from app.repository.message import MessageRepository
from app.model.message import Message
from app.model.action import Action
from app.model.document import Document

class StateHolder:
    """
    Manages the state of an agent's conversation, encompassing messages, actions, and documents.
    This class ensures encapsulation and immutability where applicable.
    
    Attributes:
        conversation_uuid (str): A unique identifier for the conversation.
    """
    def __init__(self, conversation_uuid: str, message_repository: MessageRepository, config: AgentConfig = None) -> None:
        """
        Initialize a new StateHolder instance.
        
        Args:
            conversation_uuid: Unique identifier for the conversation
            message_repository: Repository for managing messages
            config: Configuration for the state holder. If None, default config will be used.
        """
        self._conversation_uuid: str = conversation_uuid
        self._message_repository = message_repository
        self._messages: List[Message] = self._message_repository.find_by_conversation(conversation_uuid)
        self._taken_actions: List[Action] = []
        self._documents: List[Document] = []
        self._config: AgentConfig = config if config is not None else AgentConfig()

    @property
    def conversation_uuid(self) -> str:
        """The unique identifier for this conversation."""
        return self._conversation_uuid

    @property
    def messages(self) -> List[Message]:
        """Get a copy of all messages in the conversation."""
        return self._messages.copy()

    def add_message(self, content: str, role: Literal["user", "assistant"]) -> Message:
        """
        Create and add a new message to the conversation.
        
        Args:
            content: The message content
            role: The role of the message sender (user or assistant)
            
        Returns:
            Message: The created and persisted Message object
        """
        message = self._message_repository.create(
            conversation_uuid=self._conversation_uuid,
            content=content,
            role=role
        )
        self._messages.append(message)
        return message

    @property
    def taken_actions(self) -> List[Action]:
        """Get a copy of all actions taken in the conversation."""
        return self._taken_actions.copy()

    def add_action(self, action: Action) -> None:
        """
        Add a new action to the conversation.
        
        Args:
            action (Action): The action to add
        """
        self._taken_actions.append(action)

    @property
    def documents(self) -> List[Document]:
        """Get a copy of all documents in the conversation."""
        return self._documents.copy()

    def add_document(self, document: Document) -> None:
        """
        Add a new document to the conversation.
        
        Args:
            document (Document): The document to add
        """
        self._documents.append(document)

    @property
    def config(self) -> AgentConfig:
        """Get the current configuration."""
        return self._config
    
    def should_continue(self) -> bool:
        """Determine if the agent should continue processing."""
        return self._config.current_step < self._config.max_steps

    def increment_step(self) -> None:
        """Increment the current step number."""
        self._config.current_step += 1

    def reset(self) -> None:
        """Reset the state to initial values."""
        self._messages.clear()
        self._taken_actions.clear()
        self._documents.clear()
        self._config = AgentConfig() 