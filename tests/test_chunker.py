"""
Tests for document chunking functionality.
"""

import pytest

from src.chunker import create_chunks, extract_chunk_title


def test_create_chunks():
    """Test creating chunks from a document."""
    # Sample document text and metadata
    text = """
    # Sample Document
    
    This is a sample document for testing chunking functionality.
    
    ## Section 1
    
    This is the content of section 1. It contains multiple paragraphs.
    
    This is another paragraph in section 1.
    
    ## Section 2
    
    This is the content of section 2. It also contains multiple paragraphs.
    
    This is another paragraph in section 2.
    
    ## Section 3
    
    This is the content of section 3.
    """
    
    metadata = {
        "filename": "sample.md",
        "file_type": "markdown",
        "title": "Sample Document",
    }
    
    # Create chunks
    chunks = create_chunks(text, metadata)
    
    # Check if chunks were created
    assert len(chunks) > 0
    
    # Check if each chunk has the required fields
    for i, chunk in enumerate(chunks):
        assert "text" in chunk
        assert "metadata" in chunk
        
        # Check if metadata was preserved
        assert chunk["metadata"]["filename"] == "sample.md"
        assert chunk["metadata"]["file_type"] == "markdown"
        assert chunk["metadata"]["title"] == "Sample Document"
        
        # Check if chunk-specific metadata was added
        assert chunk["metadata"]["chunk_id"] == i
        assert chunk["metadata"]["chunk_total"] == len(chunks)
        assert "location" in chunk["metadata"]
        
        # Check if chunk has text content
        assert len(chunk["text"]) > 0


def test_chunk_metadata_location():
    """Test the location metadata in chunks."""
    # Create a simple document
    text = "A" * 5000  # Long enough to create multiple chunks
    metadata = {"filename": "test.txt"}
    
    # Create chunks
    chunks = create_chunks(text, metadata)
    
    # Check if there are at least 3 chunks
    assert len(chunks) >= 3
    
    # Check location markers
    assert chunks[0]["metadata"]["location"] == "beginning"
    assert chunks[-1]["metadata"]["location"] == "end"
    
    # Check middle chunks
    for i in range(1, len(chunks) - 1):
        assert chunks[i]["metadata"]["location"] == "middle"


def test_extract_chunk_title():
    """Test extracting titles from chunks."""
    # Test with markdown header
    text_with_md_header = "# Sample Header\n\nSome content."
    title = extract_chunk_title(text_with_md_header)
    assert title == "Sample Header"
    
    # Test with HTML header
    text_with_html_header = "<h1>Sample Header</h1>\n\nSome content."
    title = extract_chunk_title(text_with_html_header)
    assert title == "Sample Header"
    
    # Test with no header, just text
    text_without_header = "This is a first sentence. This is a second sentence."
    title = extract_chunk_title(text_without_header)
    assert title == "This is a first sentence."
    
    # Test with very long first sentence
    long_text = "This is a very long first sentence that exceeds the maximum title length by a significant amount. " + "Extra text. " * 20
    title = extract_chunk_title(long_text, max_length=50)
    assert len(title) <= 50
    assert title.endswith("...")
    
    # Test with empty text
    empty_text = ""
    title = extract_chunk_title(empty_text)
    assert title == "" 