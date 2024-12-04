import sqlite3
import uuid
from datetime import datetime

class DatabaseService:
    def __init__(self, db_name='chat_history.db'):
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Initialize the database and create necessary tables"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_uuid TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def store_message(self, conversation_uuid: str, role: str, content: str):
        """Store a message in the database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('INSERT INTO messages (conversation_uuid, role, content) VALUES (?, ?, ?)', 
                 (conversation_uuid, role, content))
        conn.commit()
        conn.close()

    def get_messages(self, conversation_uuid: str = None, limit: int = None):
        """Retrieve messages from the database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        query = 'SELECT role, content, timestamp FROM messages'
        params = []
        
        if conversation_uuid:
            query += ' WHERE conversation_uuid = ?'
            params.append(conversation_uuid)
            
        query += ' ORDER BY timestamp'
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
            
        c.execute(query, params)
        messages = c.fetchall()
        conn.close()
        
        return [{"role": msg[0], "content": msg[1], "timestamp": msg[2]} for msg in messages]
