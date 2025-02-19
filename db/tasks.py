from typing import List, Optional, Dict, Any

from agent.state import Task, TaskAction
from .models import TaskModel, TaskActionModel, TaskActionDocumentModel, DocumentModel
from . import connection

def save_task(task: Task) -> None:
    """Save or update a task and its actions"""
    with connection():
        # Save/update task
        task_model, created = TaskModel.get_or_create(
            uuid=task.uuid,
            defaults={
                'conversation_uuid': task.conversation_uuid,
                'name': task.name,
                'description': task.description,
                'status': task.status
            }
        )
        
        if not created:
            # Update existing task
            task_model.name = task.name
            task_model.description = task.description
            task_model.status = task.status
            task_model.save()

        # Handle actions
        existing_actions = {action.uuid: action for action in TaskActionModel.select().where(TaskActionModel.task == task_model)}
        
        for action in task.actions:
            if action.uuid in existing_actions:
                # Update existing actionw
                action_model = existing_actions[action.uuid]
                action_model.name = action.name
                action_model.tool_uuid = action.tool_uuid
                action_model.tool_action = action.tool_action
                action_model.input_payload = action.input_payload
                action_model.step = action.step
                action_model.status = action.status
                action_model.save()
                
                # Remove from existing_actions dict to track which ones to delete
                del existing_actions[action.uuid]
            else:
                # Create new action
                action_model = TaskActionModel.create(
                    uuid=action.uuid,
                    task=task_model,
                    name=action.name,
                    tool_uuid=action.tool_uuid,
                    tool_action=action.tool_action,
                    input_payload=action.input_payload,
                    step=action.step,
                    status=action.status
                )
            
            # Handle output documents
            if action.output_documents:
                # Get existing document associations
                existing_docs = {
                    doc.document.uuid: doc for doc in 
                    TaskActionDocumentModel.select().where(TaskActionDocumentModel.task_action == action_model)
                }
                
                # Track which documents we've processed
                processed_docs = set()
                
                for document in action.output_documents:
                    doc_uuid = str(document.uuid)
                    processed_docs.add(doc_uuid)
                    
                    if doc_uuid not in existing_docs:
                        # Prepare metadata by converting enums to strings
                        metadata = document.metadata.copy()
                        if metadata.get('type'):
                            metadata['type'] = metadata['type'].value if hasattr(metadata['type'], 'value') else str(metadata['type'])
                        
                        # Create new document if it doesn't exist
                        doc_model, _ = DocumentModel.get_or_create(
                            uuid=doc_uuid,
                            defaults={
                                'conversation_uuid': task.conversation_uuid,
                                'text': document.text,
                                'metadata': metadata  # Use the processed metadata
                            }
                        )
                        
                        # Create the association
                        TaskActionDocumentModel.create(
                            task_action=action_model,
                            document=doc_model
                        )
                
                # Remove document associations that are no longer present
                for old_doc_uuid in existing_docs:
                    if old_doc_uuid not in processed_docs:
                        existing_docs[old_doc_uuid].delete_instance()

        # Delete actions that no longer exist
        for old_action in existing_actions.values():
            old_action.delete_instance()

def load_tasks(conversation_uuid: str) -> List[Task]:
    """Load all tasks for a conversation"""
    with connection():
        tasks = []
        task_models = TaskModel.select().where(TaskModel.conversation_uuid == conversation_uuid)
        
        for task_model in task_models:
            # Load actions for this task
            actions = []
            action_models = (TaskActionModel
                           .select()
                           .where(TaskActionModel.task == task_model)
                           .order_by(TaskActionModel.step))
            
            for action_model in action_models:
                # Load documents for this action
                documents = []
                doc_models = (TaskActionDocumentModel
                            .select()
                            .join(DocumentModel)
                            .where(TaskActionDocumentModel.task_action == action_model))
                
                for doc_model in doc_models:
                    documents.append(Document(
                        uuid=doc_model.document.uuid,
                        conversation_uuid=doc_model.document.conversation_uuid,
                        text=doc_model.document.text,
                        metadata=doc_model.document.metadata
                    ))
                
                actions.append(TaskAction(
                    uuid=action_model.uuid,
                    name=action_model.name,
                    task_uuid=task_model.uuid,
                    tool_uuid=action_model.tool_uuid,
                    tool_action=action_model.tool_action,
                    input_payload=action_model.input_payload,
                    output_documents=documents,
                    step=action_model.step,
                    status=action_model.status
                ))
            
            tasks.append(Task(
                uuid=task_model.uuid,
                name=task_model.name,
                description=task_model.description,
                status=task_model.status,
                actions=actions
            ))
            
        return tasks

def find_task_by_uuid(task_uuid: str) -> Optional[Task]:
    """Find a specific task by UUID"""
    with connection():
        try:
            task_model = TaskModel.get(TaskModel.uuid == task_uuid)
            return load_tasks(task_model.conversation_uuid)[0]
        except TaskModel.DoesNotExist:
            return None

def update_task_status(task_uuid: str, status: str) -> None:
    """Update just the status of a task"""
    with connection():
        TaskModel.update(status=status).where(TaskModel.uuid == task_uuid).execute()

def update_task_action(task_uuid: str, action_uuid: str, updates: Dict[str, Any]) -> None:
    """Update specific fields of a task action"""
    with connection():
        TaskActionModel.update(updates).where(
            (TaskActionModel.uuid == action_uuid) & 
            (TaskActionModel.task.uuid == task_uuid)
        ).execute()
