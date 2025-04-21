"""
Tests for document processors.
"""

import os
import pytest

from src.processors.factory import get_processor
from src.processors.text import TextProcessor
from src.processors.markdown import MarkdownProcessor
from src.processors.html import HTMLProcessor


def test_text_processor(sample_text_file):
    """Test the text processor."""
    # Get the processor
    processor = get_processor(sample_text_file)
    
    # Check if the correct processor was returned
    assert isinstance(processor, TextProcessor)
    
    # Extract text
    text = processor.extract_text()
    
    # Check if the text was extracted correctly
    assert "This is a sample text document for testing." in text
    assert "It contains multiple lines of text." in text
    assert "This is the third line." in text
    
    # Extract metadata
    metadata = processor.extract_metadata()
    
    # Check if the metadata was extracted correctly
    assert metadata["file_type"] == "text"
    assert metadata["filename"] == "sample.txt"
    assert "size_kb" in metadata
    assert "word_count" in metadata
    assert metadata["word_count"] > 0
    assert "line_count" in metadata
    assert metadata["line_count"] == 3


def test_markdown_processor(sample_markdown_file):
    """Test the markdown processor."""
    # Get the processor
    processor = get_processor(sample_markdown_file)
    
    # Check if the correct processor was returned
    assert isinstance(processor, MarkdownProcessor)
    
    # Extract text
    text = processor.extract_text()
    
    # Check if the text was extracted correctly
    assert "Sample Markdown Document" in text
    assert "This is a sample markdown document for testing." in text
    assert "Section 1" in text
    assert "Content in section 1." in text
    assert "Section 2" in text
    assert "Content in section 2." in text
    
    # Extract metadata
    metadata = processor.extract_metadata()
    
    # Check if the metadata was extracted correctly
    assert metadata["file_type"] == "markdown"
    assert metadata["filename"] == "sample.md"
    assert "word_count" in metadata
    assert metadata["word_count"] > 0


def test_html_processor(sample_html_file):
    """Test the HTML processor."""
    # Get the processor
    processor = get_processor(sample_html_file)
    
    # Check if the correct processor was returned
    assert isinstance(processor, HTMLProcessor)
    
    # Extract text
    text = processor.extract_text()
    
    # Check if the text was extracted correctly
    assert "Sample HTML Document" in text
    assert "This is a sample HTML document for testing." in text
    assert "Section 1" in text
    assert "Content in section 1." in text
    assert "Section 2" in text
    assert "Content in section 2." in text
    
    # Extract metadata
    metadata = processor.extract_metadata()
    
    # Check if the metadata was extracted correctly
    assert metadata["file_type"] == "html"
    assert metadata["filename"] == "sample.html"
    assert "title" in metadata
    assert metadata["title"] == "Sample HTML Document"
    assert "description" in metadata
    assert metadata["description"] == "A sample HTML document for testing"
    assert "word_count" in metadata
    assert metadata["word_count"] > 0


def test_processor_factory(sample_text_file, sample_markdown_file, sample_html_file):
    """Test the processor factory."""
    # Get processors for different file types
    text_processor = get_processor(sample_text_file)
    markdown_processor = get_processor(sample_markdown_file)
    html_processor = get_processor(sample_html_file)
    
    # Check if the correct processors were returned
    assert isinstance(text_processor, TextProcessor)
    assert isinstance(markdown_processor, MarkdownProcessor)
    assert isinstance(html_processor, HTMLProcessor)
    
    # Test with an unsupported file type
    unsupported_file = os.path.join(os.path.dirname(sample_text_file), "unsupported.xyz")
    with open(unsupported_file, "w") as f:
        f.write("Unsupported file type")
    
    # Get processor for unsupported file type
    processor = get_processor(unsupported_file)
    
    # Check if None was returned
    assert processor is None


def test_processor_file_not_found():
    """Test handling of non-existent files."""
    with pytest.raises(FileNotFoundError):
        TextProcessor("non_existent_file.txt")
    
    with pytest.raises(FileNotFoundError):
        MarkdownProcessor("non_existent_file.md")
    
    with pytest.raises(FileNotFoundError):
        HTMLProcessor("non_existent_file.html") 