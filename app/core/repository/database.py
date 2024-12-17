import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Tuple
from pathlib import Path


class Database:
    """
    A class responsible for managing SQLite database connections and basic operations.
    Follows the Single Responsibility Principle by handling only database connectivity concerns.
    """

    def __init__(self, db_path: str = "chat_history.db"):
        """
        Initialize the Database connection manager.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self._ensure_db_directory()

    def _ensure_db_directory(self) -> None:
        """Ensure the database directory exists"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def connection(self):
        """
        Context manager for database connections.
        
        Yields:
            sqlite3.Connection: An active database connection
            
        Example:
            with database.connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
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

    def execute(self, query: str, parameters: tuple = ()) -> Optional[List[Tuple]]:
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
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, parameters)
            
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            return None

    def execute_many(self, query: str, parameters: List[tuple]) -> None:
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
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, parameters) 