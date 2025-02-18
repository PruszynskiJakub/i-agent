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
    
    try:
        # Connect to database
        db.connect()
        
        # Drop existing tables to ensure clean state
        db.drop_tables([
            TaskActionDocumentModel,
            TaskActionModel,
            TaskModel,
            ConversationDocumentModel,
            DocumentModel,
            MessageModel,
            ConversationModel
        ], safe=True)
        
        # Create tables in correct order (dependencies first)
        db.create_tables([
            ConversationModel,  # No dependencies
            MessageModel,       # Depends on Conversation
            DocumentModel,      # Depends on Conversation
            ConversationDocumentModel,  # Depends on Document and Conversation
            TaskModel,         # Depends on Conversation
            TaskActionModel,   # Depends on Task
            TaskActionDocumentModel  # Depends on TaskAction and Document
        ])
        
        print("Database initialized successfully!")
        print("Created tables:")
        print("- conversations")
        print("- messages")
        print("- documents")
        print("- conversation_documents")
        print("- tasks")
        print("- task_actions")
        print("- task_action_documents")
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        raise
    finally:
        # Close connection
        if not db.is_closed():
            db.close()

def initialize_peewee_db():
    """Initialize the database and create all required tables"""
    init_database()

if __name__ == "__main__":
    init_database()
