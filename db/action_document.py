from peewee import *
from datetime import datetime
from . import db
from .models import DocumentModel, ActionModel

class ActionDocumentModel(Model):
    action = ForeignKeyField(ActionModel, backref='action_documents')
    document = ForeignKeyField(DocumentModel, backref='document_actions')
    created_at = DateTimeField(default=datetime.utcnow)

    class Meta:
        database = db
        table_name = 'action_documents'
        primary_key = CompositeKey('action', 'document')
