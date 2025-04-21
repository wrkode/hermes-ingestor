"""
Tests for the API.
"""

import os
import json
import pytest
from fastapi.testclient import TestClient

import src.api.routes as routes


def test_health_endpoint(client, mock_qdrant_storage):
    """Test the health endpoint."""
    response = client.get("/api/health")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert data["qdrant_status"] == "healthy"


def test_status_endpoint(client, mock_qdrant_storage):
    """Test the status endpoint."""
    response = client.get("/api/status")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "document_count" in data
    assert "chunk_count" in data
    assert "storage_usage" in data


def test_ingest_file_endpoint(client, sample_text_file, mock_embedder, mock_qdrant_storage):
    """Test the ingest file endpoint."""
    # Create a test file
    with open(sample_text_file, "rb") as f:
        file_content = f.read()
    
    # Make the request
    response = client.post(
        "/api/ingest/file",
        files={"file": ("test.txt", file_content, "text/plain")}
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["file_name"] == "test.txt"
    assert data["chunks_created"] > 0


def test_ingest_file_with_metadata(client, sample_text_file, mock_embedder, mock_qdrant_storage):
    """Test the ingest file endpoint with metadata."""
    # Create a test file
    with open(sample_text_file, "rb") as f:
        file_content = f.read()
    
    # Create metadata
    metadata = {
        "source": "test",
        "category": "documentation",
        "tags": ["test", "document"]
    }
    
    # Make the request
    response = client.post(
        "/api/ingest/file",
        files={
            "file": ("test.txt", file_content, "text/plain"),
            "metadata": (None, json.dumps(metadata), "application/json")
        }
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["file_name"] == "test.txt"
    assert data["chunks_created"] > 0


def test_ingest_unsupported_file(client, mock_embedder, mock_qdrant_storage):
    """Test the ingest file endpoint with an unsupported file type."""
    # Create a test file with unsupported extension
    file_content = b"This is an unsupported file type"
    
    # Make the request
    response = client.post(
        "/api/ingest/file",
        files={"file": ("test.xyz", file_content, "application/octet-stream")}
    )
    
    # Check response
    assert response.status_code == 400
    data = response.json()
    assert "Unsupported file format" in data["detail"]


def test_ingest_multiple_files(client, sample_text_file, sample_markdown_file, mock_embedder, mock_qdrant_storage):
    """Test the ingest multiple files endpoint."""
    # Read test files
    with open(sample_text_file, "rb") as f:
        text_content = f.read()
    
    with open(sample_markdown_file, "rb") as f:
        markdown_content = f.read()
    
    # Make the request
    response = client.post(
        "/api/ingest/files",
        files=[
            ("files", ("test.txt", text_content, "text/plain")),
            ("files", ("test.md", markdown_content, "text/markdown"))
        ]
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["total_files"] == 2
    assert data["successful"] == 2
    assert data["failed"] == 0
    assert len(data["results"]) == 2


def test_delete_document_endpoint(client, sample_text_file, mock_embedder, mock_qdrant_storage):
    """Test the delete document endpoint."""
    # Process a file first
    with open(sample_text_file, "rb") as f:
        file_content = f.read()
    
    client.post(
        "/api/ingest/file",
        files={"file": ("test.txt", file_content, "text/plain")}
    )
    
    # Delete the document
    response = client.delete("/api/document/test.txt")
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["deleted_count"] > 0


def test_delete_documents_by_filter_endpoint(client, sample_text_file, mock_embedder, mock_qdrant_storage):
    """Test the delete documents by filter endpoint."""
    # Process a file first with metadata
    with open(sample_text_file, "rb") as f:
        file_content = f.read()
    
    metadata = {
        "category": "test-category"
    }
    
    client.post(
        "/api/ingest/file",
        files={
            "file": ("test.txt", file_content, "text/plain"),
            "metadata": (None, json.dumps(metadata), "application/json")
        }
    )
    
    # Delete documents by filter
    filters = {"category": "test-category"}
    response = client.post(
        "/api/document/delete",
        json=filters
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["deleted_count"] > 0 