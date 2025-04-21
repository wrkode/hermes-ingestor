"""
Tests for the ingestor.
"""

import os
import pytest
import io

from src.ingestor import Ingestor


def test_ingestor_initialization(upload_dir, mock_embedder, mock_qdrant_storage):
    """Test ingestor initialization."""
    ingestor = Ingestor()
    
    # Check if upload directory was created
    assert os.path.exists(upload_dir)


def test_process_text_file(sample_text_file, mock_embedder, mock_qdrant_storage):
    """Test processing a text file."""
    ingestor = Ingestor()
    
    # Process the file
    result = ingestor.process_file(sample_text_file)
    
    # Check the result
    assert result["success"] is True
    assert result["file_name"] == os.path.basename(sample_text_file)
    assert result["chunks_created"] > 0
    assert "processing_time" in result
    assert "chunk_ids" in result
    assert len(result["chunk_ids"]) == result["chunks_created"]


def test_process_markdown_file(sample_markdown_file, mock_embedder, mock_qdrant_storage):
    """Test processing a markdown file."""
    ingestor = Ingestor()
    
    # Process the file
    result = ingestor.process_file(sample_markdown_file)
    
    # Check the result
    assert result["success"] is True
    assert result["file_name"] == os.path.basename(sample_markdown_file)
    assert result["chunks_created"] > 0
    assert "processing_time" in result
    assert "chunk_ids" in result
    assert len(result["chunk_ids"]) == result["chunks_created"]


def test_process_html_file(sample_html_file, mock_embedder, mock_qdrant_storage):
    """Test processing an HTML file."""
    ingestor = Ingestor()
    
    # Process the file
    result = ingestor.process_file(sample_html_file)
    
    # Check the result
    assert result["success"] is True
    assert result["file_name"] == os.path.basename(sample_html_file)
    assert result["chunks_created"] > 0
    assert "processing_time" in result
    assert "chunk_ids" in result
    assert len(result["chunk_ids"]) == result["chunks_created"]


def test_process_unsupported_file(temp_dir, mock_embedder, mock_qdrant_storage):
    """Test processing an unsupported file."""
    # Create an unsupported file
    unsupported_file = os.path.join(temp_dir, "unsupported.xyz")
    with open(unsupported_file, "w") as f:
        f.write("Unsupported file type")
    
    ingestor = Ingestor()
    
    # Process the file
    result = ingestor.process_file(unsupported_file)
    
    # Check the result
    assert result["success"] is False
    assert result["file_name"] == "unsupported.xyz"
    assert "error" in result
    assert "Unsupported file type" in result["error"]


def test_process_with_additional_metadata(sample_text_file, mock_embedder, mock_qdrant_storage):
    """Test processing a file with additional metadata."""
    ingestor = Ingestor()
    
    # Additional metadata
    metadata = {
        "source": "test",
        "category": "documentation",
        "tags": ["test", "document"],
    }
    
    # Process the file with metadata
    result = ingestor.process_file(sample_text_file, metadata=metadata)
    
    # Check the result
    assert result["success"] is True
    
    # Check if metadata was included in the chunks
    storage = mock_qdrant_storage
    for chunk in storage.stored_chunks:
        assert chunk["metadata"]["source"] == "test"
        assert chunk["metadata"]["category"] == "documentation"
        assert chunk["metadata"]["tags"] == ["test", "document"]


def test_process_files(sample_text_file, sample_markdown_file, mock_embedder, mock_qdrant_storage):
    """Test processing multiple files."""
    ingestor = Ingestor()
    
    # Process multiple files
    results = ingestor.process_files([sample_text_file, sample_markdown_file])
    
    # Check the results
    assert len(results) == 2
    assert results[0]["success"] is True
    assert results[1]["success"] is True
    assert results[0]["file_name"] == os.path.basename(sample_text_file)
    assert results[1]["file_name"] == os.path.basename(sample_markdown_file)


@pytest.mark.asyncio
async def test_process_upload(temp_dir, mock_embedder, mock_qdrant_storage):
    """Test processing an uploaded file."""
    ingestor = Ingestor()
    
    # Create a file-like object
    file_content = "This is a test file for upload processing."
    file_obj = io.BytesIO(file_content.encode("utf-8"))
    
    # Process the upload
    result = await ingestor.process_upload(file_obj, "test_upload.txt")
    
    # Check the result
    assert result["success"] is True
    assert result["file_name"] == "test_upload.txt"
    assert result["chunks_created"] > 0


def test_delete_document(sample_text_file, mock_embedder, mock_qdrant_storage):
    """Test deleting a document."""
    ingestor = Ingestor()
    
    # Process a file first
    ingestor.process_file(sample_text_file)
    
    # Delete the document by filename
    result = ingestor.delete_document(os.path.basename(sample_text_file))
    
    # Check the result
    assert result["success"] is True
    assert result["deleted_count"] > 0
    assert "operation_id" in result
    
    # Try to delete a non-existent document
    result = ingestor.delete_document("non_existent_file.txt")
    
    # Check the result
    assert result["success"] is False
    assert result["deleted_count"] == 0
    assert "error" in result 