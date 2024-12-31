from typing import List, Literal, Dict

from model.action import Action
from model.document import Document
from model.message import Message
from repository.message import MessageRepository


class StateHolder:

    def __init__(self, conversation_uuid: str, message_repository: MessageRepository,
                 tools: List[Dict[str, str]]) -> None:
        self._conversation_uuid: str = conversation_uuid
        self._message_repository = message_repository
        self._messages: List[Message] = self._message_repository.find_by_conversation(conversation_uuid)
        self._taken_actions: List[Action] = []
        self._documents: List[Document] = []
        self._current_step: int = 0
        self._max_steps: int = 5
        self._tools: List[Dict[str, str]] = []

    @property
    def conversation_uuid(self) -> str:
        return self._conversation_uuid

    @property
    def messages(self) -> List[Message]:
        return self._messages.copy()

    def add_message(self, content: str, role: Literal["user", "assistant"]) -> Message:
        message = self._message_repository.create(
            conversation_uuid=self._conversation_uuid,
            content=content,
            role=role
        )
        self._messages.append(message)
        return message

    @property
    def taken_actions(self) -> List[Action]:
        return self._taken_actions.copy()

    def add_action(self, action: Action) -> None:
        self._taken_actions.append(action)

    @property
    def documents(self) -> List[Document]:
        return self._documents.copy()

    def add_document(self, document: Document) -> None:
        self._documents.append(document)

    def should_continue(self) -> bool:
        return self._current_step < self._max_steps

    def increment_step(self) -> None:
        self._current_step += 1

    def reset(self) -> None:
        self._messages.clear()
        self._taken_actions.clear()
        self._documents.clear()