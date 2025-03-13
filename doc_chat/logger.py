from typing import List, Tuple
import sqlite3
import os

class Logger:

    def __init__(self, db_path: str):
        """
        Initialize the Logger with the given database path.

        Args:
            db_path: The path to the database directory.
        """
        self.db_path = db_path
        self.database_name = "logs.db.sqlite3"
        self.__setup()

    def __setup(self) -> None:
        """Set up the database by creating the necessary directories and files."""

        # if the database already exists, do nothing
        if os.path.exists(f"{self.db_path}/{self.database_name}"):
            return

        # Create the directories
        os.makedirs(self.db_path, exist_ok=True)

        # Create SQLite connection
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()

        # Create logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log TEXT NOT NULL,
                log_type TEXT NOT NULL CHECK (log_type IN ('error', 'warning', 'info')),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.commit()
        conn.close()

    def log(self, log_type: str, log: str) -> None:
        """
        Log a message.

        Args:
            log_type: The type of the log (error, warning, info).
            log: The message to log.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO logs (log, log_type) 
            VALUES (?, ?)
        ''', (log, log_type))
        
        conn.commit()
        conn.close()

    def get_logs_after_id(self, id: int) -> List[Tuple[int, str, str, str]]:
        """
        Get all logs after a given ID.

        Args:
            id: The ID of the log.

        Returns:
            A list of tuples, where each tuple contains the ID, log, and log type.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, log, log_type, created_at FROM logs WHERE id > ?', (id,))
        logs_data = cursor.fetchall()
        conn.close()
        
        return logs_data
