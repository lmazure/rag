# Doc Chat API Endpoints

This document describes all the API endpoints available in the Doc Chat application.

## Overview

The Doc Chat application provides a set of RESTful API endpoints for managing documentation scans, chunks, and queries. The application follows standard RESTful principles:

- `GET` requests are used for retrieving data
- `POST` requests are used for creating resources or submitting data that changes server state

## Endpoints

### Home

- **URL**: `/`
- **Method**: `GET`
- **Description**: Serves the main application page
- **Parameters**: None
- **Response**: HTML page

### Fetch Documentation

- **URL**: `/fetch`
- **Method**: `POST`
- **Description**: Fetches documentation from a specified URL and its linked pages
- **Parameters**:
  - `root_url` (required): The root URL of the documentation site
- **Response**: JSON
  ```json
  {
    "message": "Fetched X URLs"
  }
  ```
- **Error Response**: 
  ```json
  {
    "error": "root_url is required"
  }
  ```

### Get All Scans

- **URL**: `/scans`
- **Method**: `GET`
- **Description**: Retrieves a list of all documentation scans
- **Parameters**: None
- **Response**: JSON array of scans, where each scan is represented as `[id, url, timestamp]`

### Get Scanned URLs

- **URL**: `/scanned_urls`
- **Method**: `GET`
- **Description**: Retrieves all URLs that were scanned for a specific scan
- **Parameters**:
  - `scan_id` (required): The ID of the scan
- **Response**: JSON array of scanned URLs, where each URL is represented as `[id, url]`
- **Error Response**:
  ```json
  {
    "error": "scan_id is required"
  }
  ```

### Get Scanned URL Content

- **URL**: `/scanned_url`
- **Method**: `GET`
- **Description**: Retrieves the content of a specific scanned URL
- **Parameters**:
  - `scanned_url_id` (required): The ID of the scanned URL
- **Response**: JSON string containing the markdown representation of the document
- **Error Response**:
  ```json
  {
    "error": "scanned_url_id is required"
  }
  ```

### Perform Chunking

- **URL**: `/perform_chunk`
- **Method**: `POST`
- **Description**: Splits the content of a scan into chunks and stores them in the vector database
- **Parameters**:
  - `scan_id` (required): The ID of the scan to chunk
- **Response**: JSON
  ```json
  {
    "message": "Ingested X chunks"
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "scan_id is required"
  }
  ```

### Get Chunks

- **URL**: `/chunks`
- **Method**: `GET`
- **Description**: Retrieves all chunks for a specific scanned URL
- **Parameters**:
  - `scanned_url_id` (required): The ID of the scanned URL
- **Response**: JSON array of chunk IDs
- **Error Response**:
  ```json
  {
    "error": "scanned_url_id is required"
  }
  ```

### Get Chunk Content

- **URL**: `/chunk_content`
- **Method**: `GET`
- **Description**: Retrieves the content of a specific chunk
- **Parameters**:
  - `chunk_id` (required): The ID of the chunk
- **Response**: JSON
  ```json
  {
    "text": "chunk text content",
    "source": "original URL source"
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "chunk_id is required"
  }
  ```
  or
  ```json
  {
    "error": "Chunk not found"
  }
  ```

### Query

- **URL**: `/query`
- **Method**: `POST`
- **Description**: Performs a semantic search on the chunks and generates a response using Together AI
- **Parameters**: None (data is sent in the request body)
- **Request Body**:
  ```json
  {
    "query": "your question here"
  }
  ```
- **Response**: JSON
  ```json
  {
    "answer": "generated answer text",
    "sources": ["URL1", "URL2", ...]
  }
  ```
- **Error Response**:
  ```json
  {
    "error": "query is required"
  }
  ```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200 OK` for successful requests
- `400 Bad Request` for requests with missing or invalid parameters
- `404 Not Found` for resources that don't exist
- `500 Internal Server Error` for server-side errors

## Usage Examples

### Typical Workflow

1. Fetch documentation: `POST /fetch?root_url=https://example.com/docs`
2. View available scans: `GET /scans`
3. Chunk the documentation: `POST /perform_chunk?scan_id=1`
4. Query the documentation: `POST /query` with body `{"query": "How do I install this library?"}`
