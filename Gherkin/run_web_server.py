from flask import Flask, jsonify
import chromadb

app = Flask(__name__)

def get_database_content(client):
    collections_data = {}
    collections = client.list_collections()
    
    for collection in collections:
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
            
        collections_data[collection.name] = documents
    
    return collections_data

@app.route('/database', methods=['GET'])
def get_database():
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
    return """
    <html>
        <head>
            <title>Chroma Database Viewer</title>
        </head>
        <body>
            <h1>Chroma Database Viewer</h1>
            <p>Access the database content at <a href="/database">/database</a></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
