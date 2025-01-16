import sqlite3

database_name = "models.db"

def setup_database(db_path: str):
    # Create SQLite connection
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    # Create a table for non-vector data
    # TODO ensure that the model and host are unique
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS models (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model TEXT NOT NULL,
            host TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def add_model_and_host(db_path: str, model: str, host: str) -> int:
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
    # Get data from SQLite
    conn = sqlite3.connect(f"{db_path}/{database_name}")
    cursor = conn.cursor()
    
    cursor.execute('SELECT id FROM models WHERE model = ? AND (host = ? OR (host IS NULL AND ? IS NULL))', (model, host, host))
    model_id = cursor.fetchone()
    conn.close()

    if model_id:
        return model_id[0]
    return None
