# Documentation Chat

A RAG application that allows users to ask questions about documentation using natural language.

## Features

🚧 to be updated 🚧 TBD

- Automatically scrapes and ingests HTML documentation from Internet using Docling
- Uses ChromaDB for vector storage
- Implements RAG using Together AI's Meta-Llama-3-70B-Instruct-Lite model
- Web interface for easy interaction
- Shows source documentation links for transparency
- Clean code organization with separate CSS and JavaScript files

## Setup

1. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate
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

5. Open a web browser and navigate to [`http://localhost:5000`](http://localhost:5000).

## Usage

🚧 to be updated 🚧 TBD

1. Enter a documentation URL and click "Fetch Documentation" to scrape and store the documentation
2. Select a scan from the dropdown menu and click "Chunk Documentation" to process it
3. Enter your question in the text input
4. Click "Ask Question" to get an AI-generated response based on the documentation

## Project Structure

The application follows a clean organization pattern:
- `app.py`: Main Flask application with API endpoints
- `scan_db.py`: Database operations for managing documentation scans
- `templates/index.html`: HTML structure of the web interface
- `static/styles.css`: CSS styles for the web interface
- `static/script.js`: JavaScript code for client-side functionality
- `data/`: Directory (created dynamically) for storing documentation and vector database

## Testing

🚧 to be updated 🚧 TBD

Run tests using pytest:
```bash
pytest
```
