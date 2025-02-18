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
    
    # Create tables if they don't exist
    db.create_tables([
        ConversationModel,
        MessageModel,
        DocumentModel,
        ConversationDocumentModel,
        TaskModel,
        TaskActionModel,
        TaskActionDocumentModel
    ], safe=True)
    
    # Close connection
    db.close()

def initialize_peewee_db():
    """Initialize the database and create all required tables"""
    init_database()

if __name__ == "__main__":
    init_database()
