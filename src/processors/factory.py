"""
Factory for creating document processors based on file type.
"""

import os
from typing import Optional

from .base import BaseProcessor
from .pdf import PDFProcessor
from .markdown import MarkdownProcessor
from .html import HTMLProcessor
from .text import TextProcessor
from .docx import DocxProcessor


def get_processor(file_path: str) -> Optional[BaseProcessor]:
    """
    Create and return the appropriate document processor for the given file.

    Args:
        file_path: Path to the document file

    Returns:
        BaseProcessor: The appropriate processor instance or None if unsupported
    """
    # Get the file extension
    _, ext = os.path.splitext(file_path.lower())
    ext = ext[1:] if ext else ""
    
    # Map extensions to processor classes
    processors = {
        "pdf": PDFProcessor,
        "md": MarkdownProcessor,
        "markdown": MarkdownProcessor,
        "html": HTMLProcessor,
        "htm": HTMLProcessor,
        "txt": TextProcessor,
        "text": TextProcessor,
        "docx": DocxProcessor,
    }
    
    # Get the processor class for the extension
    processor_class = processors.get(ext)
    
    if processor_class:
        return processor_class(file_path)
    
    return None 