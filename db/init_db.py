from peewee import SqliteDatabase
from .models import (
    ConversationModel,
    MessageModel,
    DocumentModel,
    ConversationDocumentModel,
    TaskModel,
    TaskActionModel,
    TaskActionDocumentModel
)

def init_database():
    """Initialize the database and create all required tables"""
    db = SqliteDatabase('agent.db')
    
    # Connect to database
    db.connect()
    
    # Create tables
    db.create_tables([
        ConversationModel,
        MessageModel,
        DocumentModel,
        ConversationDocumentModel,
        TaskModel,
        TaskActionModel,
        TaskActionDocumentModel
    ])
    
    # Close connection
    db.close()

if __name__ == "__main__":
    init_database()
