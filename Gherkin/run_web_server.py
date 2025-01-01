from flask import Flask, jsonify, render_template, request
import chromadb
import argparse
import sys
import os
import webbrowser
import numpy as np
from sklearn.decomposition import PCA

app = Flask(__name__)
db_path = None  # Will be set from command line argument

def get_keyword_type(collection_name: str) -> str:
    """
    Return the keyword type of a collection name.
    For example, if the collection name is "model-Outcome", the keyword type is "Outcome".
    """
    return collection_name.split('-')[-1]

def get_model(collection_name: str) -> str:
    """
    Return the model name of a collection name.
    For example, if the collection name is "model-Outcome", the model name is "model".
    """
    return '-'.join(collection_name.split('-')[:-1])

def get_collection_name(model_name: str, keyword_type: str) -> str:
    """
    Return the collection name given a model name and a keyword type.
    For example, if the model name is "model" and the keyword type is "Outcome",
    the collection name is "model-Outcome".
    """
    return f"{model_name}-{keyword_type}"

def get_list_of_models() -> list[str]:
    """
    Retrieve the list of model names from the Chroma database collections.

    Returns:
        list: The list of model names.
    """
    client = chromadb.PersistentClient(path=db_path)
    collections = client.list_collections()
    models = [get_model(collection.name) for collection in collections]
    return list(set(models))

def get_list_of_keyword_types() -> list[str]:
    """
    Retrieve the list of keyword types from the Chroma database collections.

    Returns:
        list: The list of keyword types.
    """
    client = chromadb.PersistentClient(path=db_path)
    collections = client.list_collections()
    keyword_types = [get_keyword_type(collection.name) for collection in collections]
    return list(set(keyword_types))

def get_database_content() -> dict:
    """
    Retrieve the Chroma database content.

    Returns:
        dict: A nested dictionary where the first level keys are model names,
              the second level keys are keyword types, and the values are 
              lists of documents with their IDs for each collection.
    """
    collections_data = {}

    client = chromadb.PersistentClient(path=db_path)
    collections = client.list_collections()
    for collection in collections:
        # Get the collection
        coll = client.get_collection(collection.name)

        # Get all documents in the collection
        results = coll.get(include=['documents'])

        # Initialize the data structure for the model (if not already done)
        if get_model(coll.name) not in collections_data:
            embeddings = coll.get(include=['embeddings'])
            dimension = len(embeddings['embeddings'][0])
            collections_data[get_model(coll.name)] = {'metadata': {'dimension': dimension}, 'keywords': {}}

        # Create a list of documents with their IDs
        documents = []
        for doc_id, document in zip(results['ids'], results['documents']):
            documents.append({
                'id': doc_id,
                'content': document
            })
            
        collections_data[get_model(collection.name)]['keywords'][get_keyword_type(collection.name)] = documents
    
    return collections_data

def get_projected_vectors(model_name:str, keyword_type:str) -> list:
    """
    Retrieve the projected vectors for a collection from the Chroma database.

    Args:
        model_name (str): The name of the model.
        keyword_type (str): The keyword type.

    Returns:
        list: A list of dictionaries where each dictionary contains the
              projected vector and the content of a document.
    """
    collection_name = get_collection_name(model_name, keyword_type)
    client = chromadb.PersistentClient(path=db_path)
    collection = client.get_collection(collection_name)

    # Get all items from the collection
    results = collection.get(include=['embeddings', 'documents'])
    
    # Extract embeddings
    vectors = np.array(results['embeddings'])

    # Initialize PCA
    pca = PCA(n_components=3)
    
    # Fit and transform the vectors
    projected_vectors = pca.fit_transform(vectors)

    # Create a list of documents with their IDs
    data = []
    for doc_projection, document in zip(projected_vectors, results['documents']):
        data.append({
            'projection': doc_projection.tolist(),
            'content': document
        })
    return data
    
@app.route('/models', methods=['GET'])
def get_models():
    models = get_list_of_models()
    return jsonify({
        'status': 'success',
        'data': models
    })

@app.route('/keyword_types', methods=['GET'])
def get_keyword_types():
    keyword_types = get_list_of_keyword_types()
    return jsonify({
        'status': 'success',
        'data': keyword_types
    })

@app.route('/keywords', methods=['GET'])
def get_keywords():
    try:
        data = get_database_content()
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/projections', methods=['GET'])
def get_projections():
    model = request.args.get('model')
    keyword_type = request.args.get('keyword-type')
    
    if not model or not keyword_type:
        return jsonify({'error': 'Both model and keyword-type parameters are required'}), 400
        
    try:
        projections = get_projected_vectors(model, keyword_type)
        return jsonify(projections)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/visualisation')
def visualisation():
    return render_template('visualisation.html')

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run a web server to navigate the Chroma database')
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--browser", action="store_true", help="Open the web browser after starting the server")
    args = parser.parse_args()
    db_path = args.db_path

    # Check if the path exists
    if not os.path.exists(db_path):
        print(f"Error: Path does not exist: {db_path}")
        sys.exit(1)

    # Check if it's a directory
    if not os.path.isdir(db_path):
        print(f"Error: Path is not a directory: {db_path}")
        sys.exit(1)

    # Check for essential Chroma database files/directories
    if not os.path.exists(os.path.join(db_path, 'chroma.sqlite3')):
        print(f"Error: Not a valid Chroma database at {db_path}")
        sys.exit(1)

    try:
        # Test database connection and content
        client = chromadb.PersistentClient(path=db_path)
        # Try to list collections to verify database is functional
        client.list_collections()
    except Exception as e:
        print(f"Error: Failed to connect to Chroma database at {db_path}")
        print(f"Details: {str(e)}")
        sys.exit(1)

    if args.browser:
        webbrowser.open('http://localhost:5000')

    app.run(host='0.0.0.0', port=5000, debug=True)
