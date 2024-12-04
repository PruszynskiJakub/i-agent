import sqlite3
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
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def store_message(self, role, content):
        """Store a message in the database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('INSERT INTO messages (role, content) VALUES (?, ?)', (role, content))
        conn.commit()
        conn.close()

    def get_messages(self, limit=None):
        """Retrieve messages from the database"""
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        
        query = 'SELECT role, content, timestamp FROM messages ORDER BY timestamp'
        if limit:
            query += f' LIMIT {limit}'
            
        c.execute(query)
        messages = c.fetchall()
        conn.close()
        
        return [{"role": msg[0], "content": msg[1], "timestamp": msg[2]} for msg in messages]