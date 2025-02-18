from datetime import datetime
import json
from peewee import *
from playhouse.sqlite_ext import JSONField
from . import db


class BaseModel(Model):
    class Meta:
        database = db

class ConversationModel(BaseModel):
    uuid = CharField(primary_key=True)
    name = CharField()
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'conversations'

class MessageModel(BaseModel):
    uuid = CharField(primary_key=True)
    conversation_uuid = CharField()
    content = TextField()
    role = CharField()
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'messages'

class DocumentModel(BaseModel):
    uuid = CharField(primary_key=True)
    conversation_uuid = CharField()
    text = TextField()
    metadata = JSONField()

    class Meta:
        table_name = 'documents'

class ConversationDocumentModel(BaseModel):
    conversation_uuid = CharField()
    document = ForeignKeyField(DocumentModel, backref='document_conversations')
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'conversation_documents'
        primary_key = CompositeKey('conversation_uuid', 'document')

class TaskModel(BaseModel):
    uuid = CharField(primary_key=True)
    conversation_uuid = CharField()
    name = CharField()
    description = TextField()
    status = CharField()  # pending, done, failed
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'tasks'
        indexes = (
            (('conversation_uuid',), False),  # Add index on conversation_uuid
            (('status',), False),  # Add index on status
        )

class TaskActionModel(BaseModel):
    uuid = CharField(primary_key=True)
    name = CharField()
    task = ForeignKeyField(TaskModel, backref='actions', on_delete='CASCADE')
    tool_uuid = CharField()
    tool_action = CharField()
    input_payload = JSONField(default={})
    step = IntegerField()
    status = CharField()  # pending, completed, failed
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'task_actions'

class TaskActionDocumentModel(BaseModel):
    task_action = ForeignKeyField(TaskActionModel, backref='output_documents')
    document = ForeignKeyField(DocumentModel, backref='task_actions')
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'task_action_documents'
        primary_key = CompositeKey('task_action', 'document')

