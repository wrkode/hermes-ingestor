"""
Pytest configuration file.
"""

import os
import tempfile
import shutil
import pytest
from fastapi.testclient import TestClient
import logging

from src.api.app import app
from src.storage import QdrantStorage
from src.embedder import Embedder
from src.ingestor import Ingestor
from src.config import settings


# Disable logging during tests
logging.basicConfig(level=logging.WARNING)


@pytest.fixture
def client():
    """Create a test client for the API."""
    return TestClient(app)


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def upload_dir(temp_dir):
    """Create a temporary upload directory."""
    upload_dir = os.path.join(temp_dir, "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    # Set the upload directory in settings
    original_upload_dir = settings.upload_folder
    settings.upload_folder = upload_dir
    
    yield upload_dir
    
    # Restore the original upload directory
    settings.upload_folder = original_upload_dir


@pytest.fixture
def sample_text_file(temp_dir):
    """Create a sample text file for testing."""
    file_path = os.path.join(temp_dir, "sample.txt")
    with open(file_path, "w") as f:
        f.write("This is a sample text document for testing.\n")
        f.write("It contains multiple lines of text.\n")
        f.write("This is the third line.")
    
    return file_path


@pytest.fixture
def sample_markdown_file(temp_dir):
    """Create a sample markdown file for testing."""
    file_path = os.path.join(temp_dir, "sample.md")
    with open(file_path, "w") as f:
        f.write("# Sample Markdown Document\n\n")
        f.write("This is a sample markdown document for testing.\n\n")
        f.write("## Section 1\n\n")
        f.write("Content in section 1.\n\n")
        f.write("## Section 2\n\n")
        f.write("Content in section 2.")
    
    return file_path


@pytest.fixture
def sample_html_file(temp_dir):
    """Create a sample HTML file for testing."""
    file_path = os.path.join(temp_dir, "sample.html")
    with open(file_path, "w") as f:
        f.write("<!DOCTYPE html>\n")
        f.write("<html>\n")
        f.write("<head>\n")
        f.write("  <title>Sample HTML Document</title>\n")
        f.write("  <meta name=\"description\" content=\"A sample HTML document for testing\">\n")
        f.write("</head>\n")
        f.write("<body>\n")
        f.write("  <h1>Sample HTML Document</h1>\n")
        f.write("  <p>This is a sample HTML document for testing.</p>\n")
        f.write("  <h2>Section 1</h2>\n")
        f.write("  <p>Content in section 1.</p>\n")
        f.write("  <h2>Section 2</h2>\n")
        f.write("  <p>Content in section 2.</p>\n")
        f.write("</body>\n")
        f.write("</html>")
    
    return file_path


@pytest.fixture
def mock_qdrant_storage(monkeypatch):
    """Mock the QdrantStorage class."""
    class MockQdrantStorage:
        def __init__(self, *args, **kwargs):
            self.stored_chunks = []
            self.collections = []
            
        def store_chunks(self, chunks):
            self.stored_chunks.extend(chunks)
            return ["mock-id"] * len(chunks)
        
        def count_by_filters(self, filters=None):
            return len(self.stored_chunks)
        
        def delete_by_filters(self, filters):
            self.stored_chunks = []
            return 123  # Mock operation ID
        
        def search(self, query_vector, limit=10, filters=None):
            return []
    
    monkeypatch.setattr("src.storage.QdrantStorage", MockQdrantStorage)
    return MockQdrantStorage()


@pytest.fixture
def mock_embedder(monkeypatch):
    """Mock the Embedder class."""
    class MockEmbedder:
        def __init__(self, *args, **kwargs):
            pass
            
        def embed_chunks(self, chunks, show_progress=False):
            # Add fake embeddings to chunks
            for chunk in chunks:
                chunk["embedding"] = [0.1, 0.2, 0.3]
            return chunks
        
        def embed_texts(self, texts, show_progress=False):
            # Return fake embeddings
            return [[0.1, 0.2, 0.3]] * len(texts)
    
    monkeypatch.setattr("src.embedder.Embedder", MockEmbedder)
    return MockEmbedder() 