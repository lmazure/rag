import json
from pathlib import Path
import traceback
from docling_core.types.doc.document import DoclingDocument
from docling.chunking import HybridChunker
from together import Together
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from markupsafe import escape

from vector_database import VectorDatabase
from info_database import InfoDatabase

from site_reaper import SiteReaper
from site_reaper_default import SiteReaperDefault
from site_reaper_mkdocs import SiteReaperMkdocs

from logger import Logger

from embedding_model_cohere import EmbeddingModelCohere
from embedding_model_gemini import EmbeddingModelGemini
from embedding_model_hugging_face import EmbeddingModelHuggingFace
from embedding_model_local import EmbeddingModelLocal
from embedding_model_mistral import EmbeddingModelMistral
from embedding_model_together import EmbeddingModelTogether

from chromadb.api.types import Documents, EmbeddingFunction

load_dotenv()

MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
port = 5000

site_reaper_classes = [
    SiteReaperDefault,
    SiteReaperMkdocs
]

embedding_model_classes = [
    EmbeddingModelCohere,
    EmbeddingModelGemini,
    EmbeddingModelHuggingFace,
    EmbeddingModelLocal,
    EmbeddingModelMistral,
    EmbeddingModelTogether
]

db_path = "data"
db = InfoDatabase(db_path)
cr = VectorDatabase(db_path)
logger = Logger(db_path)

app = Flask(__name__)


def build_embedding_function(host: str, model_name: str) -> EmbeddingFunction[Documents]:
    """Build the embedding function."""
    for embedding_model_class in embedding_model_classes:
        if embedding_model_class.__name__ == f"EmbeddingModel{host}":
            embedding_model_class_instance = embedding_model_class(model_name)
            return embedding_model_class_instance.build_embedding_function()
    raise ValueError(f"Invalid embedding model host: {host}")

def build_vector_collection_name(embedding_set_id: int) -> str:
    return f"docs_{embedding_set_id}"

def fetch_content(url: str, reaper: SiteReaper) -> int:
    """Fetch content from URL."""

    scan_id = db.add_scan(url, reaper.get_name())

    urls = reaper.get_urls()

    for i, url in enumerate(urls):
        logger.log('info', f"Fetched content from {url} ({i+1}/{len(urls)})")

        # Fetch and serialize the content
        doc = reaper.get_url_content(url)
        js = json.dumps(doc.export_to_dict())

        # Add the scanned URL to the database
        id = db.add_scanned_url(scan_id, url, js)

    return len(urls)

def chunk_content(scan_id: int) -> tuple[int, int]:
    """Fetch content from URLs and split into chunks."""

    chunk_set_id = db.add_chunk_set(scan_id, "HybridChunker")
    scanned_urls = db.get_all_scanned_urls(scan_id)
    chunker = HybridChunker()
    total = 0
    for i, scanned in enumerate(scanned_urls):
        scanned_url_id = scanned[0]
        doc_dict = json.loads(db.get_scanned_url_content(scanned_url_id))
        doc = DoclingDocument.model_validate(doc_dict)
        chunk_iter = chunker.chunk(doc)
        for chunk in chunk_iter:
            # enriched_text = chunker.serialize(chunk=chunk)
            db.add_chunk(chunk_set_id, scanned_url_id, chunk.text)
            total += 1
        logger.log('info', f"Chunked content of {scanned[1]} ({i+1}/{len(scanned_urls)})")
    return chunk_set_id, total

def embed_chunks(chunk_set_id: int, model: str, host: str) -> tuple[int, int]:
    """Embed the chunks of a chunk set"""
    # create an embedding set
    embedding_set_id = db.add_embedding_set(chunk_set_id, host, model)

    embedding_function = build_embedding_function(host, model)
    collection_name = build_vector_collection_name(embedding_set_id)
    cr.setup(embedding_function, collection_name)
    
    all_chunks = []
    all_metadatas = []
    all_ids = []

    # retrieve the chunks
    chunk_ids = db.get_all_chunks(chunk_set_id)

    # embed the chunks
    for chunk_id in chunk_ids:
        chunk, scanned_url_id = db.get_chunk(chunk_id)
        scanned_url = db.get_scanned_url_url(scanned_url_id)
        all_chunks.append(chunk)
        all_metadatas.append({"source": scanned_url, "embedding_set_id": embedding_set_id})
        all_ids.append(str(chunk_id))
        logger.log('info', f"Embedded chunk {chunk_id} ({len(all_chunks)}/{len(chunk_ids)})")
    cr.add_chunks(all_chunks, all_metadatas, all_ids)

    return embedding_set_id, len(all_chunks)

def generate_response(query: str, context: str) -> str:
    """Generate response using Together AI."""
    prompt = f"""Context: {context}

Question: {query}

Please provide an answer based on the context above. If the context doesn't contain enough information to answer the question, please say so."""
    client = Together()

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model=MODEL
    )
    print(response)
    return response.choices[0].message.content

@app.route('/')
def home():
    """
    Show the home page.
    """
    try:
        return render_template('index.html')
    except Exception as e:
        logger.log('error', f"/ - Failed to render home page: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to render home page', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/site_reapers', methods=['GET'])
def get_site_reapers():
    """
    Get a list of all available site reapers.

    Returns:
        A JSON array with information about each site reaper.
    """
    try:
        site_reapers = []
        
        # Get site reapers from each site reaper class
        for site_reaper_class in site_reaper_classes:
            site_reapers.append({
                "name": site_reaper_class.get_name(),
                "description": site_reaper_class.get_description()
            })
        
        return jsonify(site_reapers)
    except Exception as e:
        logger.log('error', f"/site_reapers - Failed to get site reapers: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get site reapers', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/perform_fetch', methods=['POST'])
def fetch():
    """
    Fetch content from URLs.

    Args:
        root_url: The root URL of the documentation site.

    Returns:
        A JSON response with a message indicating the number of URLs fetched.
    """
    root_url = request.args.get('root_url')
    if not root_url:
        return jsonify({'error': 'bad request', 'errorDetails': 'root_url is required'}), 400
    reaper_type = request.args.get('reaper')
    if not reaper_type:
        return jsonify({'error': 'bad request', 'errorDetails': 'reaper is required'}), 400

    try:
        site_reaper = None

        for site_reaper_class in site_reaper_classes:
            if site_reaper_class.get_name() == reaper_type:
                site_reaper = site_reaper_class(root_url)
                break

        if not site_reaper:
            return jsonify({'error': 'bad request', 'errorDetails': 'Unknown reaper'}), 400

        nb = fetch_content(root_url, site_reaper)
        return jsonify({"message": f"Fetched {nb} URLs"})
    except Exception as e:
        logger.log('error', f"/perform_fetch - Failed to fetch documentation: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to fetch documentation', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/scans', methods=['GET'])
def get_all_scans():
    """
    Get all scans.

    Returns:
        A JSON response with a list of all scans.
    """
    try:
        scans = db.get_all_scans()
        answer = [ { "id": scan[0], "root_url": scan[1], "reaper_type": scan[2], "created_at": scan[3] } for scan in scans ]
        return jsonify(answer)
    except Exception as e:
        logger.log('error', f"/scans - Failed to get scans: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get scans', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/scanned_urls', methods=['GET'])
def get_all_scanned_urls():
    """
    Get the list of scanned URLs for a given scan.

    Args:
        scan_id: The ID of the scan.

    Returns:
        A JSON response with a list of tuples, where each tuple contains the ID and URL.
    """
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'scan_id is required'}), 400
    try:
        scan_id = int(scan_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'scan_id must be an integer'}), 400
    
    try:
        urls = db.get_all_scanned_urls(scan_id)
        answer = [ { "id": url[0], "url": url[1] } for url in urls ]
        return jsonify(answer)
    except Exception as e:
        logger.log('error', f"/scanned_urls - Failed to get scanned URLs: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get scanned URLs', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/scanned_url', methods=['GET'])
def get_scanned_url():
    """
    Get a scanned URL from the database.

    Args:
        scanned_url_id: The ID of the scanned URL.

    Returns:
        A JSON response with the text of the scanned URL.
    """
    scanned_url_id = request.args.get('scanned_url_id')
    if not scanned_url_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'scanned_url_id is required'}), 400
    try:
        scanned_url_id = int(scanned_url_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'scanned_url_id must be an integer'}), 400
    
    try:
        doc_dict = json.loads(db.get_scanned_url_content(scanned_url_id))
        doc = DoclingDocument.model_validate(doc_dict)
        return jsonify(doc.export_to_markdown())
    except Exception as e:
        logger.log('error', f"/scanned_url - Failed to get scanned URL content: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get scanned URL content', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/perform_chunking', methods=['POST'])
def chunk():
    """
    Split content into chunks.

    Args:
        scan_id: The ID of the scan.

    Returns:
        A JSON response with a message indicating the number of chunks created.
    """
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'scan_id is required'}), 400
    try:
        scan_id = int(scan_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'scan_id must be an integer'}), 400

    try:
        id, nb = chunk_content(scan_id)
        return jsonify({"message": f"Created chunk set {id} containing {nb} chunks"})
    except Exception as e:
        logger.log('error', f"/perform_chunking - Failed to chunk content: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to chunk content', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500


@app.route('/chunk_sets', methods=['GET'])
def get_chunk_sets():
    """
    Get the list of chunk sets for a given scan.

    Args:
        scan_id: The ID of the scan.

    Returns:
        A JSON response with a list of chunk sets.
    """
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'scan_id is required'}), 400
    try:
        scan_id = int(scan_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'scan_id must be an integer'}), 400

    try:
        chunk_sets = db.get_all_chunk_sets(scan_id)
        answer = [ { "id": chunk_set[0], "chunker_description": chunk_set[1], "created_at": chunk_set[2] } for chunk_set in chunk_sets ]
        return jsonify(answer)
    except Exception as e:
        logger.log('error', f"/chunk_sets - Failed to get chunk sets: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get chunk sets', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/chunks', methods=['GET'])
def get_chunks():
    """
    Get the list of chunks for a given chunk set and, optionally, a scanned URL.

    Args:
        chunk_set_id: The ID of the chunk set.
        scanned_url_id: The ID of the scanned URL.

    Returns:
        A JSON response with a list of chunks.
    """
    chunk_set_id = request.args.get('chunk_set_id')
    if not chunk_set_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'chunk_set_id is required'}), 400
    try:
        chunk_set_id = int(chunk_set_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'chunk_set_id must be an integer'}), 400

    try:
        scanned_url_id = request.args.get('scanned_url_id')
        if scanned_url_id:
            try:
                scanned_url_id = int(scanned_url_id)
            except ValueError:
                return jsonify({'error': 'bad request', 'errorDetails': 'scanned_url_id must be an integer'}), 400
            chunks = db.get_all_chunks_of_scanned_url(chunk_set_id, scanned_url_id)
        else:
            chunks = db.get_all_chunks(chunk_set_id)
        return jsonify(chunks)
    except Exception as e:
        logger.log('error', f"/chunks - Failed to get chunks: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get chunks', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/chunk_content', methods=['GET'])
def get_chunk_content():
    """
    Get the content of a specific chunk.

    Args:
        chunk_id: The ID of the chunk.

    Returns:
        A JSON response with the text of the chunk.
    """
    chunk_id = request.args.get('chunk_id')
    if not chunk_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'chunk_id is required'}), 400
    try:
        chunk_id = int(chunk_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'chunk_id must be an integer'}), 400

    try:
        chunk = db.get_chunk(chunk_id)
        return jsonify({"text": chunk[0]})
    except Exception as e:
        logger.log('error', f"/chunk_content - Failed to get chunk content: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get chunk content', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/embedding_models', methods=['GET'])
def get_embedding_models():
    """
    Get a list of all available embedding models.

    Returns:
        A JSON array with information about each embedding model including host, model name, and URL.
    """
    try:
        embedding_models = []
        
        # Get models from each embedding model class
        for embedding_model_class in embedding_model_classes:
            class_name = embedding_model_class.__name__
            host = class_name.replace("EmbeddingModel", "")

            models = embedding_model_class.get_available_models()
            for model in models:
                embedding_models.append({
                    "host": host,
                    "model": model["name"],
                    "url": model["url"]
                })
        
        return jsonify(embedding_models)
    except Exception as e:
        logger.log('error', f"/embedding_models - Failed to get embedding models: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get embedding models', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/perform_embedding', methods=['POST'])
def embed():
    """
    Split content into chunks.

    Args:
        chunk_set_id: The ID of the chunk set.
        host: The host of the embedding model.
        model: The model of the embedding model.

    Returns:
        A JSON response with a message indicating the number of chunks created.
    """
    chunk_set_id = request.args.get('chunk_set_id')
    if not chunk_set_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'chunk_set_id is required'}), 400
    try:
        chunk_set_id = int(chunk_set_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'chunk_set_id must be an integer'}), 400
    host = request.args.get('host')
    if not host:
        return jsonify({'error': 'bad request', 'errorDetails': 'host is required'}), 400
    model = request.args.get('model')
    if not model:
        return jsonify({'error': 'bad request', 'errorDetails': 'model is required'}), 400

    try:
        id, nb = embed_chunks(chunk_set_id, model, host)
        return jsonify({"message": f"Created embedding set {id} containing {nb} embeddings"})
    except Exception as e:
        logger.log('error', f"/perform_embedding - Failed to embed chunks: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to embed chunks', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/embedding_sets', methods=['GET'])
def get_embedding_sets():
    """
    Get the list of embedding sets for a given chunk set.

    Args:
        chunk_set_id: The ID of the chunk set.

    Returns:
        A JSON response with a list of embedding sets.
    """
    chunk_set_id = request.args.get('chunk_set_id')
    if not chunk_set_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'chunk_set_id is required'}), 400
    try:
        chunk_set_id = int(chunk_set_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'chunk_set_id must be an integer'}), 400
    
    try:
        embedding_sets = db.get_all_embedding_sets(chunk_set_id)
        answer = [ { "id": embedding_set[0], "host": embedding_set[1], "model": embedding_set[2], "created_at": embedding_set[3] } for embedding_set in embedding_sets ]
        return jsonify(answer)
    except Exception as e:
        logger.log('error', f"/embedding_sets - Failed to get embedding sets: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get embedding sets', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/embeddings', methods=['GET'])
def get_embeddings():
    """
    Get the list of embeddings for a given embedding set.

    Args:
        embedding_set_id: The ID of the embedding set.

    Returns:
        A JSON response with a list of embeddings.
    """
    embedding_set_id = request.args.get('embedding_set_id')
    if not embedding_set_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'embedding_set_id is required'}), 400
    try:
        embedding_set_id = int(embedding_set_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'embedding_set_id must be an integer'}), 400

    try:
        embedding_set = db.get_embedding_set(embedding_set_id)
        embedding_function = build_embedding_function(embedding_set[1], embedding_set[2])
        collection_name = build_vector_collection_name(embedding_set_id)
        cr.setup(embedding_function, collection_name)
        embeddings = cr.get_all_embeddings(embedding_set_id)
        return jsonify(embeddings)
    except Exception as e:
        logger.log('error', f"/embeddings - Failed to get embeddings: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get embeddings', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/generate_answer', methods=['POST'])
def query():
    """
    Generate a response to a user question.

    Args:
        embedding_set_id: The ID of the embedding set.

    Payload:
        {
            "query": "The user question."
        }

    Returns:
        A JSON response with the answer and sources.
    """
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'bad request', 'errorDetails': 'query is required'}), 400

    embedding_set_id = request.args.get('embedding_set_id')
    if not embedding_set_id:
        return jsonify({'error': 'bad request', 'errorDetails': 'embedding_set_id is required'}), 400
    try:
        embedding_set_id = int(embedding_set_id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'embedding_set_id must be an integer'}), 400

    try:
        embedding_set = db.get_embedding_set(embedding_set_id)
        embedding_function = build_embedding_function(embedding_set[1], embedding_set[2])
        collection_name = build_vector_collection_name(embedding_set_id)
        cr.setup(embedding_function, collection_name)
        results = cr.query(user_query, embedding_set_id)

        context = "\n".join(results['documents'][0])
        print("\n---------------------------------------------------------\n".join(results['documents'][0]))
        response = generate_response(user_query, context)
        response = str(escape(response))
        response = response.replace("\n", "<br>")

        return jsonify({
            "answer": response,
            "sources": [m['source'] for m in results['metadatas'][0]]
        })

    except Exception as e:
        logger.log('error', f"/generate_answer - Failed to generate answer: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to generate answer', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/logs', methods=['GET'])
def get_logs():
    """
    Get the list of logs.

    Args:
        id: The ID of the last log already received.

    Returns:
        A JSON response with a list of logs.
    """
    id = request.args.get('id')
    if not id:
        return jsonify({'error': 'bad request', 'errorDetails': 'id is required'}), 400
    try:
        id = int(id)
    except ValueError:
        return jsonify({'error': 'bad request', 'errorDetails': 'id must be an integer'}), 400

    try:
        logs = logger.get_logs_after_id(id)
        answer = [ { "id": log[0], "log_type": log[2], "log": log[1], "created_at": log[3] } for log in logs ]
        return jsonify(answer)
    except Exception as e:
        logger.log('error', f"/logs - Failed to get logs: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get logs', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
