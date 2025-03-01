import json
from pathlib import Path
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker
from together import Together
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from markupsafe import escape

load_dotenv()

# Configure Together AI
#together.api_key = os.getenv("TOGETHER_API_KEY")
MODEL = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

app = Flask(__name__)

def get_all_html_urls(base_url: str) -> List[str]:
    """Get all HTML URLs from the documentation site."""
    urls = [ base_url ]
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    for link in soup.find_all('a'):
        href = link.get('href')
        if href and href.endswith('.html'):
            if href.startswith('http'):
                urls.append(href)
            else:
                urls.append(base_url.rstrip('/') + '/' + href.lstrip('/'))
    
    return list(set(urls))

indx = 0
def fetch_and_chunk_content(url: str) -> List[Tuple[str, str]]:
    """Fetch content from URL and split into chunks."""
    global indx
    indx += 1
    chunks = []
    converter = DocumentConverter()
    result = converter.convert(url)
    doc = result.document
    with Path(f"data/doc_{indx:05d}.json").open("w", encoding="utf-8") as fp:
        fp.write(json.dumps(doc.export_to_dict()))
    chunker = HybridChunker()
    chunk_iter = chunker.chunk(doc)
    for i, chunk in enumerate(chunk_iter):
        #print(f"=== {i} ===")
        #print(f"chunk.text:\n{repr(f'{chunk.text[:300]}…')}")
        #enriched_text = chunker.serialize(chunk=chunk)
        #print(f"chunker.serialize(chunk):\n{repr(f'{enriched_text[:300]}…')}")
        chunks.append((chunk.text, url))
    return chunks

def setup_chroma():
    """Initialize ChromaDB."""
    client = chromadb.PersistentClient(path="data/chromadb", settings=Settings(anonymized_telemetry=False))
    
    try:
        collection = client.get_collection("squash_docs")
    except:
        collection = client.create_collection("squash_docs")
    
    return collection

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
    return render_template('index.html')

@app.route('/ingest', methods=['POST'])
def ingest():

    base_url = request.args.get('url')
    if not base_url:
        return jsonify({'error': 'url is required'}), 400
    
    collection = setup_chroma()
    
    urls = get_all_html_urls(base_url)
    all_chunks = []
    all_metadatas = []
    all_ids = []
    
    for i, url in enumerate(urls):
        chunks = fetch_and_chunk_content(url)
        for j, (chunk, source_url) in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({"source": source_url})
            all_ids.append(f"chunk_{i}_{j}")

    collection.add(
        documents=all_chunks,
        metadatas=all_metadatas,
        ids=all_ids
    )
    
    return jsonify({"message": f"Ingested {len(all_chunks)} chunks from {len(urls)} URLs"})

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query')
    collection = setup_chroma()
    
    results = collection.query(
        query_texts=[user_query],
        n_results=10
    )
    
    context = "\n".join(results['documents'][0])
    print("\n---------------------------------------------------------\n".join(results['documents'][0]))
    response = generate_response(user_query, context)
    response = str(escape(response))
    response = response.replace("\n", "<br>")

    return jsonify({
        "answer": response,
        "sources": [m['source'] for m in results['metadatas'][0]]
    })

if __name__ == '__main__':
    app.run(debug=True)
