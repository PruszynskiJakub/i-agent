import sqlite3
import uuid
import json
from datetime import datetime
from contextlib import contextmanager
from typing import Optional, Any, List, Dict
from modules.types import Document, Action

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
                source TEXT,
                text TEXT NOT NULL,
                metadata TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        actions_table = '''
            CREATE TABLE IF NOT EXISTS actions (
                uuid TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                tool_uuid TEXT NOT NULL,
                payload TEXT NOT NULL,
                result TEXT,
                status TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        
        action_documents_table = '''
            CREATE TABLE IF NOT EXISTS action_documents (
                action_uuid TEXT NOT NULL,
                document_uuid TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (action_uuid, document_uuid),
                FOREIGN KEY (action_uuid) REFERENCES actions(uuid),
                FOREIGN KEY (document_uuid) REFERENCES documents(uuid)
            )
        '''
        
        self._execute_query(messages_table)
        self._execute_query(documents_table)
        self._execute_query(actions_table)
        self._execute_query(action_documents_table)

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

    def store_document(self, document: Document) -> str:
        """
        Store a document in the database
        
        Args:
            document: Document object to store
            
        Returns:
            str: UUID of the stored document
        """
        document_uuid = str(uuid.uuid4()) if 'uuid' not in document['metadata'] else document['metadata']['uuid']
        query = '''
            INSERT INTO documents (uuid, conversation_uuid, source, text, metadata)
            VALUES (?, ?, ?, ?, ?)
        '''
        self._execute_query(query, (
            document_uuid,
            document['metadata'].get('conversation_uuid', ''),
            document['metadata'].get('source', ''),
            document['text'],
            str(document['metadata'])
        ))
        return document_uuid

    def get_documents(self, conversation_uuid: str = None) -> List[Dict[str, Any]]:
        """Retrieve documents from the database"""
        query = '''
            SELECT uuid, conversation_uuid, source, text, metadata, created_at 
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
            "source": doc[2],
            "text": doc[3],
            "metadata": eval(doc[4]) if doc[4] else {},
            "created_at": doc[5]
        } for doc in documents]

    def store_action(self, action: Action) -> None:
        """Store an action and its related documents in the database"""
        # Store the action
        action_query = '''
            INSERT INTO actions (uuid, name, tool_uuid, payload, result, status)
            VALUES (?, ?, ?, ?, ?, ?)
        '''
        self._execute_query(
            action_query, 
            (
                str(action.uuid),
                action.name,
                str(action.tool_uuid),
                json.dumps(action.payload),  # Use json for proper dict serialization
                action.result,
                action.status.value  # Store the enum value as string
            )
        )
        
        # Store document relationships
        if action.documents:
            doc_query = '''
                INSERT INTO action_documents (action_uuid, document_uuid)
                VALUES (?, ?)
            '''
            for document in action.documents:
                self._execute_query(
                    doc_query,
                    (str(action.uuid), document['metadata']['uuid'])
                )

    def get_action_documents(self, action_uuid: str) -> List[Document]:
        """
        Retrieve all documents associated with an action
        
        Args:
            action_uuid: UUID of the action
            
        Returns:
            List of Document objects
        """
        query = '''
            SELECT d.* 
            FROM documents d
            JOIN action_documents ad ON d.uuid = ad.document_uuid
            WHERE ad.action_uuid = ?
        '''
        
        rows = self._execute_query(query, (action_uuid,))
        documents = []
        
        for row in rows:
            # Parse metadata string back into dict
            metadata = eval(row[4]) if row[4] else {}
            
            documents.append({
                "text": row[3],
                "metadata": metadata
            })
            
        return documents

    def get_actions(self, action_uuid: str = None) -> List[Dict[str, Any]]:
        """Retrieve actions from the database"""
        query = '''
            SELECT uuid, name, tool_uuid, payload, result, status, created_at 
            FROM actions
        '''
        params = []
        
        if action_uuid:
            query += ' WHERE uuid = ?'
            params.append(action_uuid)
            
        query += ' ORDER BY created_at DESC'
        
        actions = self._execute_query(query, tuple(params))
        return [{
            "uuid": action[0],
            "name": action[1],
            "tool_uuid": action[2],
            "payload": eval(action[3]),  # Converting string back to dict
            "result": eval(action[4]) if action[4] else None,
            "status": ActionStatus(action[5]),  # Convert string back to enum
            "created_at": action[6]
        } for action in actions]
