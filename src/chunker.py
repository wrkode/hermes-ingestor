"""
Document chunking utilities.
"""

from typing import List, Dict, Any
import re

from langchain.text_splitter import RecursiveCharacterTextSplitter

from .config import settings


def create_chunks(text: str, metadata: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Split a document into chunks with appropriate metadata.

    Args:
        text: The document text to chunk
        metadata: Metadata associated with the document

    Returns:
        List of dictionaries containing chunk text and metadata
    """
    # Create text splitter with settings from config
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunking.chunk_size,
        chunk_overlap=settings.chunking.chunk_overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    # Split the text into chunks
    texts = text_splitter.split_text(text)
    
    # Create chunks with metadata
    chunks = []
    for i, chunk_text in enumerate(texts):
        # Create a copy of the metadata for each chunk
        chunk_metadata = metadata.copy()
        
        # Add chunk-specific metadata
        chunk_metadata["chunk_id"] = i
        chunk_metadata["chunk_total"] = len(texts)
        
        # Add approximate location marker (beginning, middle, end)
        if i == 0:
            chunk_metadata["location"] = "beginning"
        elif i == len(texts) - 1:
            chunk_metadata["location"] = "end"
        else:
            chunk_metadata["location"] = "middle"
        
        # Try to extract a meaningful title for the chunk
        chunk_title = extract_chunk_title(chunk_text)
        if chunk_title:
            chunk_metadata["chunk_title"] = chunk_title
        
        # Create the chunk object
        chunks.append({
            "text": chunk_text,
            "metadata": chunk_metadata
        })
    
    return chunks


def extract_chunk_title(text: str, max_length: int = 100) -> str:
    """
    Extract a meaningful title from the chunk text.
    Tries to find headers or the first sentence.

    Args:
        text: The chunk text
        max_length: Maximum length of the title

    Returns:
        A title for the chunk
    """
    # Look for markdown/HTML style headers
    header_patterns = [
        r"^#{1,6}\s+(.+)$",                 # Markdown headers
        r"<h[1-6][^>]*>([^<]+)</h[1-6]>",   # HTML headers
    ]
    
    for pattern in header_patterns:
        match = re.search(pattern, text, re.MULTILINE)
        if match:
            title = match.group(1).strip()
            return title[:max_length] if len(title) > max_length else title
    
    # If no headers found, use the first sentence or part of it
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    if sentences:
        first_sentence = sentences[0].strip()
        if first_sentence:
            # Truncate if too long and add ellipsis
            if len(first_sentence) > max_length:
                return first_sentence[:max_length-3] + "..."
            return first_sentence
    
    # Fallback: just use the beginning of the text
    title = text.strip()
    if len(title) > max_length:
        return title[:max_length-3] + "..."
    return title 