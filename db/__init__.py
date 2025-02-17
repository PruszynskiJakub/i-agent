import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Tuple
from peewee import SqliteDatabase

db = SqliteDatabase('chat_history.db')

def initialize_peewee_db():
    """Initialize Peewee database and create all required tables"""
    from .models import (
        MessageModel, DocumentModel, TaskActionRecordModel, ActionDocumentModel,
        ConversationModel, ConversationDocumentModel
    )
    
    db.connect()
    db.create_tables([
        MessageModel,
        DocumentModel, 
        TaskActionRecordModel,
        ActionDocumentModel,
        ConversationModel,
        ConversationDocumentModel
    ])
    db.close()

# Initialize Peewee tables on module import
initialize_peewee_db()


@contextmanager
def connection():
    conn = None
    try:
        conn = sqlite3.connect('chat_history.db')
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON")
        yield conn
        conn.commit()
    except Exception as e:
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def execute(query: str, parameters: tuple = ()) -> Optional[List[Tuple]]:
    """
    Execute a SQL query and return results if any.

    Args:
        query: SQL query string
        parameters: Query parameters

    Returns:
        Optional[List[Tuple]]: Query results for SELECT queries, None for others

    Example:
        results = database.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    """
    with connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, parameters)

        if query.strip().upper().startswith('SELECT'):
            return cursor.fetchall()
        return None

def execute_many(query: str, parameters: List[tuple]) -> None:
    """
    Execute the same SQL query with different sets of parameters.

    Args:
        query: SQL query string
        parameters: List of parameter tuples

    Example:
        database.execute_many(
            "INSERT INTO users (name, email) VALUES (?, ?)",
            [("John", "john@example.com"), ("Jane", "jane@example.com")]
        )
    """
    with connection() as conn:
        cursor = conn.cursor()
        cursor.executemany(query, parameters)
