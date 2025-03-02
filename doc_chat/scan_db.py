import sqlite3
import os

database_name = "scans.db.sqlite3"

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
    
    # Create a table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scanned_urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL
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

def add_url(db_path: str, url: str) -> int:
    """
    Add a scanned URL to the database.

    Args:
        db_path: The path to the database directory.
        url: The URL of the scan.

    Returns:
        The ID of the inserted model.
    """
    # Store regular data in SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scanned_urls (url) 
        VALUES (?)
    ''', (url,))
    
    # Get the ID of the inserted model
    id = cursor.lastrowid
    conn.commit()
    assert id is not None
    conn.close()
    
    return id
        

def get_url(db_path: str, url_id: int) -> str:
    """
    Get a scanned URL from the database.

    Args:
        db_path: The path to the database directory.
        url_id: The ID of the URL.

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
