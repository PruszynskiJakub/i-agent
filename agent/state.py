from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from db.message import find_messages_by_conversation, save_message
from logger.logger import log_info
from models.document import Document
from models.message import Message
from models.state import Task, AgentPhase, Thoughts, TaskAction
from utils.message import create_message


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

    final_answer: Optional[str] = None

    @staticmethod
    def create_or_restore_state(conversation_uuid: str):
        from db.tasks import load_tasks
        initial_state = AgentState(
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
        log_info(
            f"Initial state - Tasks: {len(initial_state.tasks)}, Documents: {len(initial_state.conversation_documents)}, Messages: {len(initial_state.messages)}")

        return initial_state

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

    def update_tasks(self, tasks: List[Task]):
        for task in tasks:
            from db.tasks import save_task
            save_task(task)
        return self.copy(tasks=tasks)



    @property
    def user_query(self) -> str:
        """Returns the content of the last user message"""
        for message in reversed(self.messages):
            if message.role == "user":
                return message.content
        return ""

    model_config = ConfigDict(frozen=True)

    def copy(self, **kwargs) -> 'AgentState':
        return self.model_copy(update=kwargs)
