import sqlite3
import uuid
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Any, List, Dict

class DatabaseService:
    def __init__(self, db_name='chat_history.db'):
        self.db_name = db_name
        self.init_db()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _execute_query(self, query: str, params: tuple = ()) -> Optional[List[tuple]]:
        """Execute a query and return results if any"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            return None

    def init_db(self):
        """Initialize the database and create necessary tables"""
        messages_table = '''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_uuid TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        documents_table = '''
            CREATE TABLE IF NOT EXISTS documents (
                uuid TEXT PRIMARY KEY,
                conversation_uuid TEXT,
                name TEXT,
                source TEXT,
                mime_type TEXT,
                text TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        self._execute_query(messages_table)
        self._execute_query(documents_table)

    def store_message(self, conversation_uuid: str, role: str, content: str) -> None:
        """Store a message in the database"""
        query = 'INSERT INTO messages (conversation_uuid, role, content) VALUES (?, ?, ?)'
        self._execute_query(query, (conversation_uuid, role, content))

    def get_messages(self, conversation_uuid: str = None, limit: int = None) -> List[Dict[str, Any]]:
        """Retrieve messages from the database"""
        query = 'SELECT role, content, timestamp FROM messages'
        params = []
        
        if conversation_uuid:
            query += ' WHERE conversation_uuid = ?'
            params.append(conversation_uuid)
            
        query += ' ORDER BY timestamp'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
            
        messages = self._execute_query(query, tuple(params))
        return [{"role": msg[0], "content": msg[1], "timestamp": msg[2]} for msg in messages]

    def store_document(self, conversation_uuid: str, name: str, source: str, mime_type: str, text: str) -> str:
        """Store a document in the database"""
        document_uuid = str(uuid.uuid4())
        query = '''
            INSERT INTO documents (uuid, conversation_uuid, name, source, mime_type, text)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self._execute_query(query, (document_uuid, conversation_uuid, name, source, mime_type, text))
        return document_uuid

    def get_documents(self, conversation_uuid: str = None) -> List[Dict[str, Any]]:
        """Retrieve documents from the database"""
        query = '''
            SELECT uuid, conversation_uuid, name, source, mime_type, text, created_at 
            FROM documents
        '''
        params = []
        
        if conversation_uuid:
            query += ' WHERE conversation_uuid = ?'
            params.append(conversation_uuid)
            
        query += ' ORDER BY created_at DESC'
        
        documents = self._execute_query(query, tuple(params))
        return [{
            "uuid": doc[0],
            "conversation_uuid": doc[1],
            "name": doc[2],
            "source": doc[3],
            "mime_type": doc[4],
            "text": doc[5],
            "created_at": doc[6]
        } for doc in documents]
