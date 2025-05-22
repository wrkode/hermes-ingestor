# Hermes API Documentation

## Authentication
All API endpoints require authentication using an API key. Include the API key in the `X-API-Key` header with each request:

```bash
curl -H "X-API-Key: your-api-key" http://localhost:8000/api/health
```

## Rate Limiting
API requests are rate-limited to prevent abuse. The current limits are:
- 100 requests per minute per IP address
- 1000 requests per hour per API key

## Endpoints

### Health Check
```http
GET /api/health
```
Returns the health status of the service and its dependencies.

Response:
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "qdrant_status": "healthy"
}
```

### Document Upload
```http
POST /api/ingest/file
Content-Type: multipart/form-data
```
Upload and process a single document.

Request:
- `file`: The document file (PDF, DOCX, TXT, MD)
- `metadata`: Optional JSON metadata (string)

Response:
```json
{
    "success": true,
    "file_name": "document.pdf",
    "chunks_created": 10,
    "processing_time": 1.5
}
```

### Batch Upload
```http
POST /api/ingest/files
Content-Type: multipart/form-data
```
Upload and process multiple documents.

Request:
- `files`: Multiple document files
- `metadata`: Optional JSON metadata (string)

Response:
```json
{
    "total_files": 3,
    "successful": 2,
    "failed": 1,
    "results": [...]
}
```

### URL Ingestion
```http
POST /api/ingest/url
Content-Type: application/json
```
Download and process a document from a URL.

Request:
```json
{
    "url": "https://example.com/document.pdf",
    "metadata": {
        "source": "web",
        "tags": ["example", "pdf"]
    }
}
```

Response:
```json
{
    "success": true,
    "message": "Processing started for URL: https://example.com/document.pdf",
    "file_name": "document.pdf"
}
```

### Service Status
```http
GET /api/status
```
Get the current status of the service, including document and chunk counts.

Response:
```json
{
    "status": "healthy",
    "document_count": 100,
    "chunk_count": 1000,
    "storage_usage": {
        "documents": 100,
        "chunks": 1000
    }
}
```

## Error Responses
All endpoints return standard HTTP status codes and error messages:

```json
{
    "detail": "Error message"
}
```

Common status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## WebSocket Events
The service provides real-time updates via WebSocket connections:

```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws');

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('Processing update:', data);
};
```

Event types:
- `processing_started`: Document processing has begun
- `processing_progress`: Processing progress update
- `processing_complete`: Processing has completed
- `processing_error`: An error occurred during processing 