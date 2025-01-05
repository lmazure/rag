from flask import Flask, jsonify, render_template, request
import chromadb
import argparse
import sys
import os
import webbrowser
import numpy as np
from sklearn.decomposition import PCA
import common

app = Flask(__name__)
db_path = None  # Will be set from command line argument

def get_database_content() -> dict:

    collections_data = {}

    client = chromadb.PersistentClient(path=db_path)
    collection_names = client.list_collections()
    for name in collection_names:
        # Get the collection
        coll = client.get_collection(name)
        model = common.get_model(coll.name)
        project = common.get_project_name(coll.name)
        keyword_type = common.get_keyword_type(coll.name)

        # Get all documents in the collection
        results = coll.get(include=['documents'])

        # Initialize the data structure for the model (if not already done)
        if model not in collections_data:
            embeddings = coll.get(include=['embeddings'])
            dimension = len(embeddings['embeddings'][0])
            collections_data[model] = {'metadata': {'dimension': dimension}, 'projects': {project: {'keywords': {}}}}

        # Create a list of documents with their IDs
        documents = []
        for doc_id, document in zip(results['ids'], results['documents']):
            documents.append({
                'id': doc_id,
                'content': document
            })
            
        collections_data[model]['projects'][project]['keywords'][keyword_type] = documents
    
    return collections_data

def get_projected_vectors(model:str, project:str, keyword_type:str) -> list:

    collection_name = common.get_collection_name(model, project, keyword_type)
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
    project = request.args.get('project')
    keyword_type = request.args.get('keyword-type')
    
    if not model or not project or not keyword_type:
        return jsonify({'error': 'Both model, project, and keyword-type parameters are required'}), 400
        
    try:
        projections = get_projected_vectors(model, project, keyword_type)
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
    parser = argparse.ArgumentParser(description='Run a web server (on port 5000) to navigate the Chroma database')
    parser.add_argument("--db_path", default="./chromadb/database", help="Path to the Chroma database (default: ./chromadb/database)")
    parser.add_argument("--browser", action="store_true", help="Open the Web Browser after starting the server")
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
