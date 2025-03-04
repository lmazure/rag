from typing import List, Tuple
import sqlite3
import os

database_name = "history.db.sqlite3"

def setup_database(db_path: str) -> None:
    """
    Set up the database of the scanned URLs by creating the necessary directories and files.

    Args:
        db_path: The path to the database directory.
    """
    # Create the directorie
    os.makedirs(db_path, exist_ok=True)

    # Create SQLite connection
    conn = sqlite3.connect(f"{db_path}/{database_name}")
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

    # Create chunks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chunk TEXT NOT NULL,
            FOREIGN KEY (scanned_url_id) REFERENCES scanned_urls (id)
        )
    ''')

    conn.commit()
    conn.close()

def delete_database(db_path: str) -> None:
    """
    Delete the database.

    Args:
        db_path: The path to the database directory.
    """
    os.remove(f"{db_path}/{database_name}")

def add_scan(db_path: str, root_url: str) -> int:
    """
    Add a scan to the database.

    Args:
        db_path: The path to the database directory.
        root_url: The root URL of the scan.

    Returns:
        The ID of the inserted scan.
    """
    # Store regular data in SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scans (root_url) 
        VALUES (?)
    ''', (root_url,))
    
    # Get the ID of the inserted scan
    id = cursor.lastrowid
    conn.commit()
    assert id is not None
    conn.close()
    
    return id

def get_scan(db_path: str, scan_id: int) -> Tuple[int, str]:
    """
    Get a scan from the database.

    Args:
        db_path: The path to the database directory.
        scan_id: The ID of the scan.

    Returns:
        A tuple of (scan_id, root_url).
    """
    # Get data from SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM scans WHERE id = ?', (scan_id,))
    scan_data = cursor.fetchone()
    conn.close()
    
    return scan_data

def get_all_scans(db_path: str) -> List[Tuple[int, str]]:
    """
    Get all scans from the database.

    Args:
        db_path: The path to the database directory.

    Returns:
        A list of tuples, where each tuple contains the ID and root URL.
    """
    # Get data from SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM scans')
    scans_data = cursor.fetchall()
    conn.close()
    
    return scans_data

def add_scanned_url(db_path: str, scan_id: int, url: str) -> int:
    """
    Add a scanned URL to the database.

    Args:
        db_path: The path to the database directory.
        scan_id: The ID of the scan.
        url: The URL of the scan.

    Returns:
        The ID of the inserted model.
    """
    # Store regular data in SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scanned_urls (scan_id, url) 
        VALUES (?, ?)
    ''', (scan_id, url))
    
    # Get the ID of the inserted model
    id = cursor.lastrowid
    conn.commit()
    assert id is not None
    conn.close()
    
    return id
        

def get_scanned_url(db_path: str, url_id: int) -> str:
    """
    Get a scanned URL from the database.

    Args:
        db_path: The path to the database directory.
        url_id: The ID of the scanned URL.

    Returns:
        The URL as a string.

    Raises:
        Exception: If the URL is not found.
    """
    # Get data from SQLite 
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM scanned_urls WHERE id = ?', (url_id,))
    url_data = cursor.fetchone()
    conn.close()
    
    if url_data:
        return url_data[1]
    raise Exception(f"URL {url_id} not found")

def get_all_scanned_urls(db_path: str, scan_id: int) -> List[Tuple[int, str]]:
    """
    Get all scanned URLs of a scan from the database.

    Args:
        db_path: The path to the database directory.
        scan_id: The ID of the scan.

    Returns:
        A list of tuples, where each tuple contains the ID and URL.
    """
    # Get data from SQLite 
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM scanned_urls WHERE scan_id = ?', (scan_id,))
    urls_data = cursor.fetchall()
    conn.close()
    
    print(urls_data)
    return urls_data

def add_chunk(db_path: str, scanned_url_id: int, chunk: str) -> int:
    """
    Add a chunk to the database.

    Args:
        db_path: The path to the database directory.
        scanned_url_id: The ID of the scanned URL.
        chunk: The chunk to add.

    Returns:
        The ID of the inserted chunk.
    """
    # Store regular data in SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO chunks (scanned_url_id, chunk) 
        VALUES (?, ?)
    ''', (scanned_url_id, chunk))
    
    # Get the ID of the inserted chunk
    id = cursor.lastrowid
    conn.commit()
    assert id is not None
    conn.close()
    
    return id

def get_chunk(db_path: str, chunk_id: int) -> str:
    """
    Get a chunk from the database.

    Args:
        db_path: The path to the database directory.
        chunk_id: The ID of the chunk.

    Returns:
        The chunk as a string.
    """
    # Get data from SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM chunks WHERE id = ?', (chunk_id,))
    chunk_data = cursor.fetchone()
    conn.close()
    
    if chunk_data:
        return chunk_data[1]
    raise Exception(f"Chunk {chunk_id} not found")

def get_all_chunks(db_path: str, scanned_url_id: int) -> List[int]:
    """
    Get all chunks of a scanned URL from the database.

    Args:
        db_path: The path to the database directory.
        scanned_url_id: The ID of the scanned URL.

    Returns:
        A list of the IDs of the chunks.
    """
    # Get data from SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM chunks WHERE scanned_url_id = ?', (scanned_url_id,))
    chunks_data = cursor.fetchall()
    conn.close()
    
    return [chunk[0] for chunk in chunks_data]
