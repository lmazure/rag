# Squash Documentation Chat

A RAG (Retrieval-Augmented Generation) application that allows users to ask questions about Squash documentation using natural language.

## Features

- Automatically scrapes and ingests HTML documentation from Squash
- Uses ChromaDB for vector storage
- Implements RAG using Together AI's Meta-Llama-3-70B-Instruct-Lite model
- Web interface for easy interaction
- Shows source documentation links for transparency

## Setup

1. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Create a `.env` file with your Together AI API key:
    ```
    TOGETHER_API_KEY=your_api_key_here
    ```

4. Run the application:
    ```bash
    python app.py
    ```

    There will be some warnings `Token indices sequence length is longer than the specified maximum sequence length for this model (518 > 512). Running this sequence through the model will result in indexing errors`. You can ignore them, see https://github.com/DS4SD/docling-core/issues/119.

5. Open a web browser and navigate to `http://localhost:5000`

## Usage

1. Click the "Ingest Documentation" button to scrape and store the Squash documentation
2. Enter your question in the text input
3. Click "Ask Question" to get an AI-generated response based on the documentation

## Testing

Run tests using pytest:
```bash
pytest
```
