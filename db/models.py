from datetime import datetime
import json
from peewee import *
from uuid import UUID
from . import db

class JSONField(TextField):
    def python_value(self, value):
        if value is not None:
            return json.loads(value)
        return {}

    def db_value(self, value):
        if value is not None:
            return json.dumps(value)
        return '{}'

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

class ActionRecordModel(BaseModel):
    uuid = CharField(primary_key=True)
    name = CharField()
    tool = CharField()
    tool_uuid = CharField(null=True)
    payload = JSONField()
    status = CharField()
    conversation_uuid = CharField()
    step_description = CharField(default='')
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'actions'

class ActionDocumentModel(BaseModel):
    action = ForeignKeyField(ActionRecordModel, backref='action_documents')
    document = ForeignKeyField(DocumentModel, backref='document_actions')
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'action_documents'
        primary_key = CompositeKey('action', 'document')

class ConversationDocumentModel(BaseModel):
    conversation_uuid = CharField()
    document = ForeignKeyField(DocumentModel, backref='document_conversations')
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        table_name = 'conversation_documents'
        primary_key = CompositeKey('conversation_uuid', 'document')

