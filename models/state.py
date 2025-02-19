from dataclasses import field
from enum import Enum
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, ConfigDict

from db.message import find_messages_by_conversation, save_message
from models.document import Document
from models.message import Message
from utils.message import create_message


class AgentPhase(str, Enum):
    INTENT = "intent"
    PLAN = "plan"
    DEFINE = "define"
    DECIDE = "decide"
    EXECUTE = "execute"
    ANSWER = "answer"


class ToolThought(BaseModel):
    """A single potential tool usage or action idea."""
    query: str
    tool_name: str

    model_config = ConfigDict(frozen=True)


class Thoughts(BaseModel):
    """Internal reasoning plus recommended tool candidates."""
    tool_thoughts: List[ToolThought] = field(default_factory=list)
    user_intent: str = ""

    model_config = ConfigDict(frozen=True)


class TaskAction(BaseModel):
    uuid: str
    name: str
    tool_uuid: str
    task_uuid: str
    tool_action: str
    input_payload: Dict[str, Any] = field(default_factory=dict)
    output_documents: List[Document] = field(default_factory=list)
    step: int
    status: str  # pending, done, failed

    model_config = ConfigDict(frozen=True)


class Task(BaseModel):
    uuid: str
    name: str
    description: str
    actions: List[TaskAction]
    status: str  # pending or done
    conversation_uuid: Optional[str] = None

    model_config = ConfigDict(frozen=True)


class AgentState(BaseModel):
    conversation_uuid: str
    messages: List[Message]
    tasks: List[Task]
    conversation_documents: List[Document]

    phase: AgentPhase
    current_step: int
    max_steps: int
    thoughts: Thoughts
    current_task: Optional[Task]
    current_action: Optional[TaskAction]
    current_tool: Optional[str]
    tool_dynamic_context: Optional[str]

    final_answer:Optional[str] = None

    @staticmethod
    def create_or_restore_state(conversation_uuid: str):
        from db.tasks import load_tasks
        return AgentState(
            conversation_uuid=conversation_uuid,
            messages=find_messages_by_conversation(conversation_uuid),
            tasks=load_tasks(conversation_uuid),
            conversation_documents=[],  # load_conversation_documents(conversation_uuid),
            current_step=0,
            max_steps=4,
            phase=AgentPhase.INTENT,
            current_task=None,
            current_action=None,
            thoughts=Thoughts(),
            tool_dynamic_context=None,
            current_tool=None,
            final_answer=None
        )

    def update_phase(self, new_phase: AgentPhase):
        return self.copy(phase=new_phase)

    def set_tool_dynamic_context(self, context: str):
        return self.copy(tool_dynamic_context=context)

    def update_thoughts(self, thoughts):
        return self.copy(thoughts=thoughts)

    def update_current_tool(self, tool):
        return self.copy(current_tool=tool)

    def update_final_answer(self, final_answer):
        return self.copy(final_answer=final_answer)

    def add_message(self, content, role):
        message = create_message(self.conversation_uuid, content, role)
        save_message(message)
        return self.copy(messages=[*self.messages, message])

    def complete_thinking_step(self):
        return self.copy(
            current_step=self.current_step + 1,
            tool_dynamic_context="",
            current_task=None,
            current_action=None,
            current_tool=None,
        )

    def should_continue(self) -> bool:
        return self.current_step < self.max_steps

    @property
    def user_query(self) -> str:
        """Returns the content of the last user message"""
        for message in reversed(self.messages):
            if message.role == "user":
                return message.content
        return ""

    @property
    def assistant_response(self) -> str:
        """Returns the content of the last assistant message"""
        for message in reversed(self.messages):
            if message.role == "assistant":
                return message.content
        return ""

    model_config = ConfigDict(frozen=True)

    def copy(self, **kwargs) -> 'AgentState':
        return self.model_copy(update=kwargs)
