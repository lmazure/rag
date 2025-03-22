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
from mkdocs_site_reaper import MkdocsSiteReaper
from logger import Logger

load_dotenv()

MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
port = 5000

db_path = "data"
db = InfoDatabase(db_path)
cr = VectorDatabase(db_path)
logger = Logger(db_path)

app = Flask(__name__)

def compute_scanned_url_filename(id: int) -> str:
    """Compute the filename for a scanned URL."""
    return f"{db_path}/scanned_urls/{(id%100):02d}/doc_{id:06d}.json"

def fetch_content(scan_id: int, url: str, reaper: SiteReaper) -> None:
    """Fetch content from URL."""

    # Fetch the content
    doc = reaper.get_url_content(url)

    # Add the scanned URL to the database
    id = db.add_scanned_url(scan_id, url)

    # Save the document to a JSON file
    filename = compute_scanned_url_filename(id)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with Path(filename).open("w", encoding="utf-8") as fp:
        fp.write(json.dumps(doc.export_to_dict()))

    return

def chunk_content(scan_id: int) -> int:
    """Fetch content from URLs and split into chunks."""
    chunk_set_id = db.add_chunk_set(scan_id, "HybridChunker")
    scanned_urls = db.get_all_scanned_urls(scan_id)
    chunker = HybridChunker()
    for i, scanned in enumerate(scanned_urls):
        scanned_url_id = scanned[0]
        with Path(compute_scanned_url_filename(scanned_url_id)).open("r", encoding="utf-8") as fp:
            doc_dict = json.loads(fp.read())
            doc = DoclingDocument.model_validate(doc_dict)
        chunk_iter = chunker.chunk(doc)
        for chunk in chunk_iter:
            # enriched_text = chunker.serialize(chunk=chunk)
            db.add_chunk(chunk_set_id, scanned_url_id, chunk.text)
        logger.log('info', f"Chunked content of {scanned[1]} ({i+1}/{len(scanned_urls)})")
    return i

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
        return jsonify({'error': 'root_url is required'}), 400
    reaper_type = request.args.get('reaper')
    if not reaper_type:
        return jsonify({'error': 'reaper is required'}), 400

    try:

        if reaper_type == 'mkdocs':
            reaper = MkdocsSiteReaper(root_url)
        elif reaper_type == 'default':
            reaper = SiteReaper(root_url)
        else:
            return jsonify({'error': 'Invalid reaper type'}), 400

        scan_id = db.add_scan(root_url, reaper_type + " reaper")

        urls = reaper.get_urls()

        for i, url in enumerate(urls):
            fetch_content(scan_id, url, reaper)
            logger.log('info', f"Fetched content from {url} ({i+1}/{len(urls)})")

        return jsonify({"message": f"Fetched {len(urls)} URLs"})
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
        Returns an error message if 'scan_id' is not provided.
    """
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({'error': 'scan_id is required'}), 400
    try:
        scan_id = int(scan_id)
    except ValueError:
        return jsonify({'error': 'scan_id must be an integer'}), 400
    
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
        Returns an error message if 'scanned_url_id' is not provided.
    """
    scanned_url_id = request.args.get('scanned_url_id')
    if not scanned_url_id:
        return jsonify({'error': 'scanned_url_id is required'}), 400
    try:
        scanned_url_id = int(scanned_url_id)
    except ValueError:
        return jsonify({'error': 'scanned_url_id must be an integer'}), 400
    
    try:
        with Path(compute_scanned_url_filename(scanned_url_id)).open("r", encoding="utf-8") as fp:
            doc_dict = json.loads(fp.read())
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
        Returns an error message if 'scan_id' is not provided.
    """
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({'error': 'scan_id is required'}), 400
    try:
        scan_id = int(scan_id)
    except ValueError:
        return jsonify({'error': 'scan_id must be an integer'}), 400

    try:
        nb = chunk_content(scan_id)
        return jsonify({"message": f"Created {nb} chunks"})
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
        Returns an error message if 'scan_id' is not provided.
    """
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({'error': 'scan_id is required'}), 400
    try:
        scan_id = int(scan_id)
    except ValueError:
        return jsonify({'error': 'scan_id must be an integer'}), 400

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
        Returns an error message if 'chunk_set_id' is not provided.
    """
    chunk_set_id = request.args.get('chunk_set_id')
    if not chunk_set_id:
        return jsonify({'error': 'chunk_set_id is required'}), 400
    try:
        chunk_set_id = int(chunk_set_id)
    except ValueError:
        return jsonify({'error': 'chunk_set_id must be an integer'}), 400

    try:
        scanned_url_id = request.args.get('scanned_url_id')
        if scanned_url_id:
            try:
                scanned_url_id = int(scanned_url_id)
            except ValueError:
                return jsonify({'error': 'scanned_url_id must be an integer'}), 400
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
        Returns an error message if 'chunk_id' is not provided.
    """
    chunk_id = request.args.get('chunk_id')
    if not chunk_id:
        return jsonify({'error': 'chunk_id is required'}), 400
    try:
        chunk_id = int(chunk_id)
    except ValueError:
        return jsonify({'error': 'chunk_id must be an integer'}), 400

    try:
        chunk = db.get_chunk(chunk_id)
        return jsonify({"text": chunk[0]})
    except Exception as e:
        logger.log('error', f"/chunk_content - Failed to get chunk content: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get chunk content', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/perform_embedding', methods=['POST'])
def embed():
    """
    Split content into chunks.

    Args:
        chunk_set_id: The ID of the chunk set.

    Returns:
        A JSON response with a message indicating the number of chunks created.
        Returns an error message if 'chunk_set_id' is not provided.
    """
    chunk_set_id = request.args.get('chunk_set_id')
    if not chunk_set_id:
        return jsonify({'error': 'chunk_set_id is required'}), 400
    try:
        chunk_set_id = int(chunk_set_id)
    except ValueError:
        return jsonify({'error': 'chunk_set_id must be an integer'}), 400

    try:
        cr.setup()
        
        all_chunks = []
        all_metadatas = []
        all_ids = []

        # retrieve the chunks
        chunk_ids = db.get_all_chunks(chunk_set_id)

        # create an embedding set
        embedding_set_id = db.add_embedding_set(chunk_set_id, "default embedder")

        # embed the chunks
        for chunk_id in chunk_ids:
            chunk, scanned_url_id = db.get_chunk(chunk_id)
            scanned_url = db.get_scanned_url(scanned_url_id)
            all_chunks.append(chunk)
            all_metadatas.append({"source": scanned_url, "embedding_set_id": embedding_set_id})
            all_ids.append(str(chunk_id))
            logger.log('info', f"Embedded chunk {chunk_id} ({len(all_chunks)}/{len(chunk_ids)})")
        cr.add_chunks(all_chunks, all_metadatas, all_ids)

        return jsonify({"message": f"Embedded {len(all_chunks)} chunks"})
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
        Returns an error message if 'chunk_set_id' is not provided.
    """
    chunk_set_id = request.args.get('chunk_set_id')
    if not chunk_set_id:
        return jsonify({'error': 'chunk_set_id is required'}), 400
    try:
        chunk_set_id = int(chunk_set_id)
    except ValueError:
        return jsonify({'error': 'chunk_set_id must be an integer'}), 400
    
    try:
        embedding_sets = db.get_all_embedding_sets(chunk_set_id)
        answer = [ { "id": embedding_set[0], "embedder_description": embedding_set[1], "created_at": embedding_set[2] } for embedding_set in embedding_sets ]
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
        Returns an error message if 'embedding_set_id' is not provided.
    """
    embedding_set_id = request.args.get('embedding_set_id')
    if not embedding_set_id:
        return jsonify({'error': 'embedding_set_id is required'}), 400
    try:
        embedding_set_id = int(embedding_set_id)
    except ValueError:
        return jsonify({'error': 'embedding_set_id must be an integer'}), 400

    try:
        cr.setup()
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
        query: The user question.

    Returns:
        A JSON response with the answer and sources.
        Returns an error message if 'query' is not provided.
    """
    user_query = request.json.get('query')
    if not user_query:
        return jsonify({'error': 'query is required'}), 400

    try:
        results = cr.query(user_query)

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
        return jsonify({'error': 'id is required'}), 400
    try:
        id = int(id)
    except ValueError:
        return jsonify({'error': 'id must be an integer'}), 400

    try:
        logs = logger.get_logs_after_id(id)
        answer = [ { "id": log[0], "log_type": log[2], "log": log[1], "created_at": log[3] } for log in logs ]
        return jsonify(answer)
    except Exception as e:
        logger.log('error', f"/logs - Failed to get logs: {str(e)}\n{traceback.format_exc()}")
        return jsonify({'error': 'Failed to get logs', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)
