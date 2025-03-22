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
        self.database_name = "info.db.sqlite3"
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

        # Create scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                root_url TEXT NOT NULL,
                reaper_type TEXT NOT NULL,
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
                scanned_url_id INTEGER NOT NULL,
                FOREIGN KEY (chunk_set_id) REFERENCES chunk_sets (id)
            )
        ''')

        # Create embedding sets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS embedding_sets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chunk_set_id INTEGER NOT NULL,
                embedder_description TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (chunk_set_id) REFERENCES chunk_sets (id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_scan(self, root_url: str, reaper_type: str) -> int:
        """
        Add a scan.

        Args:
            root_url: The root URL of the scan.
            reaper_type: The type of reaper to use.

        Returns:
            The ID of the inserted scan.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO scans (root_url, reaper_type) 
            VALUES (?, ?)
        ''', (root_url, reaper_type))
        
        id = cursor.lastrowid
        conn.commit()
        assert id is not None
        conn.close()
        
        return id

    def get_scan(self, scan_id: int) -> Tuple[int, str, str, str]:
        """
        Get a scan.

        Args:
            scan_id: The ID of the scan.

        Returns:
            A tuple of (scan_id, root_url, reaper_type, created_at).
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, root_url, reaper_type, created_at FROM scans WHERE id = ?', (scan_id,))
        scan_data = cursor.fetchone()
        conn.close()
        
        return scan_data

    def get_all_scans(self) -> List[Tuple[int, str, str, str]]:
        """
        Get all scans.

        Returns:
            A list of tuples, where each tuple contains the ID, root URL, reaper type, and created at.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, root_url, reaper_type, created_at FROM scans')
        scans_data = cursor.fetchall()
        conn.close()
        
        return scans_data

    def add_scanned_url(self, scan_id: int, url: str) -> int:
        """
        Add a scanned URL.

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
        Get a scanned URL.

        Args:
            url_id: The ID of the scanned URL.

        Returns:
            The URL as a string.

        Raises:
            Exception: If the URL is not found.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, url FROM scanned_urls WHERE id = ?', (url_id,))
        url_data = cursor.fetchone()
        conn.close()
        
        if url_data:
            return url_data[1]
        raise Exception(f"URL {url_id} not found")

    def get_all_scanned_urls(self, scan_id: int) -> List[Tuple[int, str]]:
        """
        Get all scanned URLs of a scan.

        Args:
            scan_id: The ID of the scan.

        Returns:
            A list of tuples, where each tuple contains the ID and URL.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, url FROM scanned_urls WHERE scan_id = ?', (scan_id,))
        urls_data = cursor.fetchall()
        conn.close()
        
        return urls_data

    def add_chunk_set(self, scan_id: int, chunker_description: str) -> int:
        """
        Add a chunk set.

        Args:
            scan_id: The ID of the scan.
            chunker_description: The description of the chunker.

        Returns:
            The ID of the inserted chunk set.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chunk_sets (scan_id, chunker_description) 
            VALUES (?, ?)
        ''', (scan_id, chunker_description))
        
        id = cursor.lastrowid
        conn.commit()
        assert id is not None
        conn.close()
        
        return id

    def get_all_chunk_sets(self, scan_id: int) -> List[Tuple[int, str, str]]:
        """
        Get all chunk sets for a given scan.

        Args:
            scan_id: The ID of the scan.

        Returns:
            A list of tuples, where each tuple contains the ID and chunker description.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, chunker_description, created_at FROM chunk_sets WHERE scan_id = ?', (scan_id,))
        chunk_sets_data = cursor.fetchall()
        conn.close()
        
        return chunk_sets_data

    def add_chunk(self, chunk_set_id: int, scanned_url_id: int, chunk: str) -> int:
        """
        Add a chunk.

        Args:
            chunk_set_id: The ID of the chunk set.
            scanned_url_id: The ID of the scanned URL.
            chunk: The chunk to add.

        Returns:
            The ID of the inserted chunk.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO chunks (chunk_set_id, scanned_url_id, chunk) 
            VALUES (?, ?, ?)
        ''', (chunk_set_id, scanned_url_id, chunk))
        
        id = cursor.lastrowid
        conn.commit()
        assert id is not None
        conn.close()
        
        return id

    def get_chunk(self, chunk_id: int) -> Tuple[str, int]:
        """
        Get a chunk.

        Args:
            chunk_id: The ID of the chunk.

        Returns:
            The chunk as a string and the ID of the scanned URL.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('SELECT chunk, scanned_url_id FROM chunks WHERE id = ?', (chunk_id,))
        chunk_data = cursor.fetchone()
        conn.close()
        
        if chunk_data:
            return chunk_data[0], chunk_data[1]
        raise Exception(f"Chunk {chunk_id} not found")

    def get_all_chunks(self, chunk_set_id: int) -> List[int]:
        """
        Get all chunks of a chunk set.

        Args:
            chunk_set_id: The ID of the chunk set.

        Returns:
            A list of the IDs of the chunks of the chunk set.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM chunks WHERE chunk_set_id = ?', (chunk_set_id,))
        chunks_data = cursor.fetchall()
        conn.close()
        
        return [chunk[0] for chunk in chunks_data]

    def get_all_chunks_of_scanned_url(self, chunk_set_id: int, scanned_url_id: int) -> List[str]:
        """
        Get all chunks of a scanned URL in a given chunk set.

        Args:
            chunk_set_id: The ID of the chunk set.
            scanned_url_id: The ID of the scanned URL.

        Returns:
            A list of the IDs of the chunks of the scanned URL.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()

        cursor.execute('SELECT id FROM chunks WHERE chunk_set_id = ? AND scanned_url_id = ?', (chunk_set_id, scanned_url_id))
        chunks_data = cursor.fetchall()
        conn.close()
        
        return [chunk[0] for chunk in chunks_data]

    def add_embedding_set(self, chunk_set_id: int, embedder_description: str) -> int:
        """
        Add an embedding set.

        Args:
            chunk_set_id: The ID of the chunk set.
            embedder_description: The description of the embedder.

        Returns:
            The ID of the inserted embedding set.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO embedding_sets (chunk_set_id, embedder_description) 
            VALUES (?, ?)
        ''', (chunk_set_id, embedder_description))
        
        id = cursor.lastrowid
        conn.commit()
        assert id is not None
        conn.close()
        
        return id

    def get_all_embedding_sets(self, chunk_set_id: int) -> List[Tuple[int, str, str]]:
        """
        Get all embedding sets of a chunk set.

        Args:
            chunk_set_id: The ID of the chunk set.

        Returns:
            A list of the IDs of the embedding sets of the chunk set.
        """
        conn = sqlite3.connect(f"{self.db_path}/{self.database_name}")
        cursor = conn.cursor()

        cursor.execute('SELECT id, embedder_description, created_at FROM embedding_sets WHERE chunk_set_id = ?', (chunk_set_id,))
        embedding_sets_data = cursor.fetchall()
        conn.close()
        
        return embedding_sets_data
