import os
import pytest
import sqlite3
from ..model_db import (
    setup_database,
    delete_database,
    add_model_and_host,
    get_model_and_host,
    get_model_id,
    database_name
)

@pytest.fixture
def test_db_path(tmp_path):
    """Fixture to provide a temporary database path."""
    return str(tmp_path)

def test_setup_database(test_db_path):
    """Test database setup functionality."""
    setup_database(test_db_path)
    
    # Check if database file exists
    assert os.path.exists(f"{test_db_path}/{database_name}")
    
    # Check if tables are created correctly
    conn = sqlite3.connect(f"{test_db_path}/{database_name}")
    cursor = conn.cursor()
    
    # Check if models table exists and has correct schema
    cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='models'")
    table_schema = cursor.fetchone()[0]
    assert "id INTEGER PRIMARY KEY" in table_schema
    assert "model TEXT NOT NULL" in table_schema
    assert "host TEXT" in table_schema
    
    conn.close()

def test_add_and_get_model(test_db_path):
    """Test adding and retrieving a model."""
    setup_database(test_db_path)
    
    # Test adding a model with host
    model_id = add_model_and_host(test_db_path, "gpt-4", "example_com")
    assert isinstance(model_id, int)
    
    # Test retrieving the model
    model_data = get_model_and_host(test_db_path, model_id)
    assert model_data["model"] == "gpt-4"
    assert model_data["host"] == "example_com"
    
    # Test adding a model without host
    model_id2 = add_model_and_host(test_db_path, "gpt-3.5", None)
    model_data2 = get_model_and_host(test_db_path, model_id2)
    assert model_data2["model"] == "gpt-3.5"
    assert model_data2["host"] is None

def test_duplicate_remote_model_error(test_db_path):
    """Test that adding duplicate remote models raises an exception."""
    setup_database(test_db_path)
    
    add_model_and_host(test_db_path, "gpt-4", "example_com")
    
    with pytest.raises(Exception) as exc_info:
        add_model_and_host(test_db_path, "gpt-4", "example_com")
    assert "already exists" in str(exc_info.value)

def test_duplicate_local_model_host_error(test_db_path):
    """Test that adding duplicate local models raises an exception."""
    setup_database(test_db_path)
    
    add_model_and_host(test_db_path, "gpt-4", None)
    
    with pytest.raises(Exception) as exc_info:
        add_model_and_host(test_db_path, "gpt-4", None)
    assert "already exists" in str(exc_info.value)

def test_duplicate_local_andremote_model(test_db_path):
    """Test adding same local and remote model."""
    setup_database(test_db_path)
    
    add_model_and_host(test_db_path, "gpt-4", "example_com")
    add_model_and_host(test_db_path, "gpt-4", None)

def test_get_remote_model_id(test_db_path):
    """Test getting remote model ID."""
    setup_database(test_db_path)
    
    # Add a model and verify we can get its ID
    original_id = add_model_and_host(test_db_path, "gpt-4", "example_com")
    retrieved_id = get_model_id(test_db_path, "gpt-4", "example_com")
    assert original_id == retrieved_id
    
    # Test with non-existent models
    assert get_model_id(test_db_path, "non-existent", "example_com") is None
    assert get_model_id(test_db_path, "gpt-4", "other_com") is None
    assert get_model_id(test_db_path, "gpt-4", None) is None

def test_get_local_model_id(test_db_path):
    """Test getting local model ID."""
    setup_database(test_db_path)
    
    # Add a model and verify we can get its ID
    original_id = add_model_and_host(test_db_path, "gpt-4", None)
    retrieved_id = get_model_id(test_db_path, "gpt-4", None)
    assert original_id == retrieved_id
    
    # Test with non-existent model
    assert get_model_id(test_db_path, "non-existent", None) is None

def test_get_nonexistent_model(test_db_path):
    """Test getting a non-existent model raises an exception."""
    setup_database(test_db_path)
    
    with pytest.raises(Exception) as exc_info:
        get_model_and_host(test_db_path, 999)
    assert "not found" in str(exc_info.value)

def test_delete_database(test_db_path):
    """Test database deletion."""
    setup_database(test_db_path)
    assert os.path.exists(f"{test_db_path}/{database_name}")
    
    delete_database(test_db_path)
    assert not os.path.exists(f"{test_db_path}/{database_name}")
