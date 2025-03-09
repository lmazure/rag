from typing import List, Tuple
import sqlite3
import os

class InfoDatabase:
    def __init__(self, db_path: str):
        """
        Initialize the InfoDatabase with the given database path.

        Args:
            db_path: The path to the database directory.
        """
        self.db_path = db_path
        self.database_name = "history.db.sqlite3"
        self.setup()

    def setup(self) -> None:
        """Set up the database of the scanned URLs by creating the necessary directories and files."""
        # Create the directories
        os.makedirs(self.db_path, exist_ok=True)

        # Create SQLite connection
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()

        # Create scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                root_url TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Create scanned URLs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scanned_urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                url TEXT NOT NULL,
                FOREIGN KEY (scan_id) REFERENCES scans (id)
            )
        ''')

        # Create chunk sets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunk_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                scan_id INTEGER NOT NULL,
                chunker_description TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id) REFERENCES scans (id)
            )
        ''')

        # Create chunks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk TEXT NOT NULL,
                chunk_set_id INTEGER NOT NULL,
                FOREIGN KEY (chunk_set_id) REFERENCES chunk_sets (id)
            )
        ''')

        # Create embedding sets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embedding_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_set_id INTEGER NOT NULL,
                embedder_description TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP;
                FOREIGN KEY (scan_id) REFERENCES scans (id)
            )
        ''')

        conn.commit()
        conn.close()

    def delete_database(self) -> None:
        """Delete the database."""
        os.remove(f"{self.db_path}/{self.database_name}")

    def add_scan(self, root_url: str) -> int:
        """
        Add a scan to the database.

        Args:
            root_url: The root URL of the scan.

        Returns:
            The ID of the inserted scan.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scans (root_url) 
            VALUES (?)
        ''', (root_url,))
        
        id = cursor.lastrowid
        conn.commit()
        assert id is not None
        conn.close()
        
        return id

    def get_scan(self, scan_id: int) -> Tuple[int, str]:
        """
        Get a scan from the database.

        Args:
            scan_id: The ID of the scan.

        Returns:
            A tuple of (scan_id, root_url).
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
        scan_data = cursor.fetchone()
        conn.close()
        
        return scan_data

    def get_all_scans(self) -> List[Tuple[int, str]]:
        """
        Get all scans from the database.

        Returns:
            A list of tuples, where each tuple contains the ID and root URL.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scans')
        scans_data = cursor.fetchall()
        conn.close()
        
        return scans_data

    def add_scanned_url(self, scan_id: int, url: str) -> int:
        """
        Add a scanned URL to the database.

        Args:
            scan_id: The ID of the scan.
            url: The URL of the scan.

        Returns:
            The ID of the inserted model.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scanned_urls (scan_id, url) 
            VALUES (?, ?)
        ''', (scan_id, url))
        
        id = cursor.lastrowid
        conn.commit()
        assert id is not None
        conn.close()
        
        return id

    def get_scanned_url(self, url_id: int) -> str:
        """
        Get a scanned URL from the database.

        Args:
            url_id: The ID of the scanned URL.

        Returns:
            The URL as a string.

        Raises:
            Exception: If the URL is not found.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scanned_urls WHERE id = ?', (url_id,))
        url_data = cursor.fetchone()
        conn.close()
        
        if url_data:
            return url_data[2]
        raise Exception(f"URL {url_id} not found")

    def get_all_scanned_urls(self, scan_id: int) -> List[Tuple[int, str]]:
        """
        Get all scanned URLs of a scan from the database.

        Args:
            scan_id: The ID of the scan.

        Returns:
            A list of tuples, where each tuple contains the ID and URL.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM scanned_urls WHERE scan_id = ?', (scan_id,))
        urls_data = cursor.fetchall()
        conn.close()
        
        return [(url[0], url[2]) for url in urls_data]

    def add_chunk(self, scanned_url_id: int, chunk: str) -> int:
        """
        Add a chunk to the database.

        Args:
            scanned_url_id: The ID of the scanned URL.
            chunk: The chunk to add.

        Returns:
            The ID of the inserted chunk.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chunks (scanned_url_id, chunk) 
            VALUES (?, ?)
        ''', (scanned_url_id, chunk))
        
        id = cursor.lastrowid
        conn.commit()
        assert id is not None
        conn.close()
        
        return id

    def get_chunk(self, chunk_id: int) -> str:
        """
        Get a chunk from the database.

        Args:
            chunk_id: The ID of the chunk.

        Returns:
            The chunk as a string.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT chunk FROM chunks WHERE id = ?', (chunk_id,))
        chunk_data = cursor.fetchone()
        conn.close()
        
        if chunk_data:
            return chunk_data[0]
        raise Exception(f"Chunk {chunk_id} not found")

    def get_all_chunks(self, scanned_url_id: int) -> List[str]:
        """
        Get all chunks of a scanned URL from the database.

        Args:
            scanned_url_id: The ID of the scanned URL.

        Returns:
            A list of the IDs of the chunks of the scanned URL.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM chunks WHERE scanned_url_id = ?', (scanned_url_id,))
        chunks_data = cursor.fetchall()
        conn.close()
        
        return [chunk[0] for chunk in chunks_data]
