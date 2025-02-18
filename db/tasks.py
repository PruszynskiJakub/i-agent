from typing import List
from peewee import prefetch
from db.models import TaskModel, TaskActionModel, DocumentModel, TaskActionDocumentModel


def load_tasks(conversation_id: str) -> List[TaskModel]:
    # Query all tasks for the given conversation.
    tasks_query = TaskModel.select().where(TaskModel.conversation == conversation_id)
    
    # Prepare queries for the related models.
    actions_query = TaskActionModel.select()
    action_documents_query = TaskActionDocumentModel.select()
    documents_query = DocumentModel.select()
    
    # Use peewee prefetch to load related TaskActionModel and their documents.
    tasks_with_relations = prefetch(
        tasks_query,
        actions_query,
        action_documents_query,
        documents_query
    )
    return list(tasks_with_relations)
