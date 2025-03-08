import json
from pathlib import Path
import traceback
from typing import List, Tuple
from docling_core.types.doc.document import DoclingDocument
import requests
from bs4 import BeautifulSoup
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from together import Together
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from markupsafe import escape

from vector_database import VectorDatabase
from info_database import InfoDatabase

load_dotenv()

# Configure Together AI
MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"
port = 5000

db_path = "data"
db = InfoDatabase(db_path)
cr = VectorDatabase(db_path)

app = Flask(__name__)

def get_all_html_urls(base_url: str) -> List[str]:
    """Get all HTML URLs from the documentation site."""
    urls = [ base_url ]
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and (href.endswith('.html') or href.endswith('.htm')):
            if href.startswith('http'):
                urls.append(href)
            else:
                urls.append(base_url.rstrip('/') + '/' + href.lstrip('/'))
    
    return list(set(urls))

def compute_scanned_url_filename(id: int) -> str:
    """Compute the filename for a scanned URL."""
    return f"{db_path}/scanned_urls/{(id%100):02d}/doc_{id:06d}.json"

def fetch_content(scan_id: int, url: str) -> None:
    """Fetch content from URL."""

    # Add the scanned URL to the database
    id = db.add_scanned_url(scan_id, url)

    # Fetch the content
    converter = DocumentConverter()
    result = converter.convert(url)
    doc = result.document

    # Save the document to a JSON file
    filename = compute_scanned_url_filename(id)
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    with Path(filename).open("w", encoding="utf-8") as fp:
        fp.write(json.dumps(doc.export_to_dict()))

    return

def chunk_content(scan_id: int) -> List[Tuple[str, str, int]]:
    """Fetch content from URLs and split into chunks."""
    scanned_urls = db.get_all_scanned_urls(scan_id)
    chunker = HybridChunker()
    chunks = []
    for scanned in scanned_urls:
        scanned_url_id = scanned[0]
        scanned_url = scanned[1]
        with Path(compute_scanned_url_filename(scanned_url_id)).open("r", encoding="utf-8") as fp:
            doc_dict = json.loads(fp.read())
            doc = DoclingDocument.model_validate(doc_dict)
        chunk_iter = chunker.chunk(doc)
        for i, chunk in enumerate(chunk_iter):
            print(f"=== {i} ===")
            print(f"chunk.text:\n{repr(f'{chunk.text[:300]}…')}")
            enriched_text = chunker.serialize(chunk=chunk)
            print(f"chunker.serialize(chunk):\n{repr(f'{enriched_text[:300]}…')}")
            chunk_id = db.add_chunk(scanned_url_id, chunk.text)
            chunks.append((chunk.text, scanned_url,chunk_id))
    return chunks

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
    return render_template('index.html')

@app.route('/fetch', methods=['POST'])
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

    try:
        scan_id = db.add_scan(root_url)

        urls = get_all_html_urls(root_url)

        for url in urls:
            fetch_content(scan_id, url)

        return jsonify({"message": f"Fetched {len(urls)} URLs"})
    except Exception as e:
        return jsonify({'error': 'Failed to fetch documentation', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

@app.route('/scans', methods=['GET'])
def get_all_scans():
    """
    Get all scans.

    Returns:
        A JSON response with a list of all scans.
    """
    scans = db.get_all_scans()
    return jsonify(scans)

@app.route('/scanned_urls', methods=['GET'])
def get_all_scanned_urls():
    """
    Get all scanned URLs for a given scan ID.

    Returns:
        A JSON response with a list of tuples, where each tuple contains the ID and URL.
        Returns an error message if 'scan_id' is not provided.
    """
    scan_id = request.args.get('scan_id')
    if not scan_id:
        return jsonify({'error': 'scan_id is required'}), 400
    urls = db.get_all_scanned_urls(scan_id)
    return jsonify(urls)

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
    with Path(compute_scanned_url_filename(int(scanned_url_id))).open("r", encoding="utf-8") as fp:
        doc_dict = json.loads(fp.read())
        doc = DoclingDocument.model_validate(doc_dict)
    return jsonify(doc.export_to_markdown())

@app.route('/perform_chunk', methods=['POST'])
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

    cr.setup()
    
    all_chunks = []
    all_metadatas = []
    all_ids = []

    chunks = chunk_content(int(scan_id))
    for (chunk, url, chunk_id) in chunks:
        all_chunks.append(chunk)
        all_metadatas.append({"source": url})
        all_ids.append(str(chunk_id))
    cr.add_chunks(all_chunks, all_metadatas, all_ids)

    return jsonify({"message": f"Ingested {len(all_chunks)} chunks"})

@app.route('/chunks', methods=['GET'])
def get_chunks():
    """
    Get chunks for a given scanned URL.

    Args:
        scanned_url_id: The ID of the scanned URL.

    Returns:
        A JSON response with a list of chunks.
        Returns an error message if 'scanned_url_id' is not provided.
    """
    scanned_url_id = request.args.get('scanned_url_id')
    if not scanned_url_id:
        return jsonify({'error': 'scanned_url_id is required'}), 400
    
    chunks = db.get_all_chunks(int(scanned_url_id))
    
    return jsonify(chunks)

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

    chunk = db.get_chunk(int(chunk_id))
    return jsonify({"text": chunk})

@app.route('/query', methods=['POST'])
def query():
    """
    Generate a response using Together AI.

    Args:
        query: The user query.

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
        return jsonify({'error': 'Failed to generate answer', 'errorDetails': str(e), 'stackTrace': traceback.format_exc()}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=True)