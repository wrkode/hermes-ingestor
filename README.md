# Hermes Ingestor

A microservice for processing and embedding documents for knowledge bases.

## Overview

Hermes Ingestor is a part of a larger LLM-powered self-service knowledge base platform. The ingestor handles:

1. Document processing (PDF, Markdown, HTML, Text, DOCX)
2. Text extraction
3. Document chunking
4. Vector embedding generation
5. Storage in Qdrant vector database

## Features

- Support for multiple document formats (PDF, Markdown, HTML, Text, DOCX)
- Document chunking with metadata preservation
- Text embedding using sentence transformers
- Integration with Qdrant vector database
- RESTful API for document ingestion and management
- Kubernetes-ready containerization

## Installation

### Requirements

- Python 3.8 or higher
- Qdrant (local instance or cloud)
- Dependencies listed in `requirements.txt`

### Setup

```bash
# Clone the repository
git clone https://github.com/wrkode/hermes-ingestor.git
cd hermes-ingestor

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

## Configuration

The service is configured using environment variables:

```bash
# Core settings
DEBUG=False
UPLOAD_FOLDER=uploads
MAX_FILE_SIZE_MB=50

# Qdrant settings
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION=documents
QDRANT_PREFER_GRPC=True
QDRANT_API_KEY=  # For Qdrant Cloud

# Embedding settings
EMBEDDING_MODEL=all-MiniLM-L6-v2
EMBEDDING_BATCH_SIZE=32
EMBEDDING_DIMENSIONS=384

# Chunking settings
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Usage

### Running the Service

```bash
# Run the service
python -m src.main

# Run with custom host and port
python -m src.main --host 0.0.0.0 --port 8080

# Run in debug mode
python -m src.main --debug
```

### API Endpoints

#### Document Ingestion

- `POST /api/ingest/file` - Upload and process a single document
- `POST /api/ingest/files` - Upload and process multiple documents

#### Document Management

- `DELETE /api/document/{filename}` - Delete a document by filename
- `POST /api/document/delete` - Delete documents by metadata filter

#### Service Information

- `GET /api/health` - Health check
- `GET /api/status` - Service status

## Docker

Build and run the service using Docker:

```bash
# Build the Docker image
docker build -t hermes-ingestor .

# Run the container
docker run -p 8000:8000 \
  -e QDRANT_HOST=host.docker.internal \
  -e QDRANT_PORT=6333 \
  hermes-ingestor

# Alternatively
docker compose up --build
```

## Kubernetes

Example Kubernetes deployment configurations are available in the `k8s/` directory.

## License

Apache 2.0