import sqlite3
import os

database_name = "models.db.sqlite3"

def setup_database(db_path: str):
    """
    Set up the database by creating the necessary directories and files.

    Args:
        db_path: The path to the database directory.
    """
    # Create the directories
    os.makedirs(db_path, exist_ok=True)

    # Create SQLite connection
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    # Create a table for non-vector data
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            host TEXT
        )
    ''')

    # Ensure that the model and host are unique
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS unique_model_host ON models (model, host)
        WHERE host IS NOT NULL
    ''')
    cursor.execute('''
        CREATE UNIQUE INDEX IF NOT EXISTS unique_model_null_host ON models (model)
        WHERE host IS NULL;
    ''')
    
    conn.commit()
    conn.close()

def add_model_and_host(db_path: str, model: str, host: str) -> int:
    """
    Add a model and host to the SQLite database.

    Args:
        db_path: The path to the database directory.
        model: The name of the model.
        host: The host of the model (may be None).

    Returns:
        The ID of the inserted model.

    Raises:
        Exception: If the model already exists.
    """
    # Store regular data in SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO models (model, host) 
            VALUES (?, ?)
        ''', (model, host))
        
        # Get the ID of the inserted model
        id = cursor.lastrowid
        conn.commit()
        
        return id
        
    except sqlite3.IntegrityError:
        print(f"Model {model} at {host} already exists")
        raise Exception(f"Model {model} at {host} already exists")
    finally:
        conn.close()

def get_model_and_host(db_path: str, model_id: int) -> dict[str, str]:
    """
    Get a model and host from the SQLite database.

    Args:
        db_path: The path to the database directory.
        model_id: The ID of the model.

    Returns:
        The model as a dictionary with 'id', 'model', and 'host' keys ('host' may be None).

    Raises:
        Exception: If the model is not found.
    """
    # Get data from SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM models WHERE id = ?', (model_id,))
    model_data = cursor.fetchone()
    conn.close()
    
    if model_data:
        return {
            'id': model_data[0],
            'model': model_data[1],
            'host': model_data[2]
        }
    raise Exception(f"Model {model_id} not found")

def get_model_id(db_path: str, model: str, host: str) -> int:
    """
    Get the ID of a model in the SQLite database.

    Args:
        db_path: The path to the database directory.
        model: The name of the model.
        host: The host of the model (may be None).

    Returns:
        The ID of the model.

    Raises:
        Exception: If the model is not found.
    """
    # Get data from SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM models WHERE model = ? AND (host = ? OR (host IS NULL AND ? IS NULL))', (model, host, host))
    model_id = cursor.fetchone()
    conn.close()

    if model_id:
        return model_id[0]
    return None
