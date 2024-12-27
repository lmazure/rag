from flask import Flask, jsonify, render_template
import chromadb

app = Flask(__name__)

def get_keyword_type(str: str) -> str:
    """
    Return the keyword type of a collection name.
    For example, if the collection name is "model-Outcome", the keyword type is "Outcome".
    """
    return str.split('-')[-1]

def get_model(str: str) -> str:
    """
    Return the model name of a collection name.
    For example, if the collection name is "model-Outcome", the model name is "model".
    """
    return '-'.join(str.split('-')[:-1])

def get_list_of_models():
    """
    Retrieve the list of model names from the Chroma database collections.

    Returns:
        list: The list of model names.
    """
    client = chromadb.PersistentClient(path="./chromadb/database")
    collections = client.list_collections()
    models = [get_model(collection.name) for collection in collections]
    return list(set(models))

def get_list_of_keyword_types():
    """
    Retrieve the list of keyword types from the Chroma database collections.

    Returns:
        list: The list of keyword types.
    """
    client = chromadb.PersistentClient(path="./chromadb/database")
    collections = client.list_collections()
    keyword_types = [get_keyword_type(collection.name) for collection in collections]
    return list(set(keyword_types))

def get_database_content(client):
    """
    Retrieve the Chroma database content.

    Args:
        client: The Chroma database client.

    Returns:
        dict: A nested dictionary where the first level keys are model names,
              the second level keys are keyword types, and the values are 
              lists of documents with their IDs for each collection.
    """
    collections_data = {}
    
    collections = client.list_collections()
    for collection in collections:
        if get_model(collection.name) not in collections_data:
            collections_data[get_model(collection.name)] = {}

        # Get the collection
        coll = client.get_collection(collection.name)
        
        # Get all documents in the collection
        results = coll.get(include=['documents'])
        
        # Create a list of documents with their IDs
        documents = []
        for doc_id, document in zip(results['ids'], results['documents']):
            documents.append({
                'id': doc_id,
                'content': document
            })
            
        collections_data[get_model(collection.name)][get_keyword_type(collection.name)] = documents
    
    return collections_data

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
        client = chromadb.PersistentClient(path="./chromadb/database")
        data = get_database_content(client)
        return jsonify({
            'status': 'success',
            'data': data
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
