"""
Text embedding utilities.
"""

from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from .config import settings


class Embedder:
    """Class for creating text embeddings."""

    def __init__(self, model_name: str = None):
        """
        Initialize the embedder with a model.

        Args:
            model_name: Name of the embedding model to use
        """
        self.model_name = model_name or settings.embedding.model_name
        self.model = SentenceTransformer(self.model_name)
        self.batch_size = settings.embedding.batch_size
        self.dimension = settings.embedding.dimensions
    
    def embed_texts(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """
        Create embeddings for a list of texts.

        Args:
            texts: List of texts to embed
            show_progress: Whether to show a progress bar

        Returns:
            numpy.ndarray: Array of embeddings
        """
        if not texts:
            return np.array([])
        
        # Use tqdm for progress bar if requested
        iterator = tqdm(range(0, len(texts), self.batch_size), desc="Embedding") if show_progress else range(0, len(texts), self.batch_size)
        
        all_embeddings = []
        for batch_start in iterator:
            batch_end = min(batch_start + self.batch_size, len(texts))
            batch_texts = texts[batch_start:batch_end]
            
            # Create embeddings for the batch
            batch_embeddings = self.model.encode(batch_texts, convert_to_numpy=True)
            all_embeddings.append(batch_embeddings)
        
        # Concatenate all batches
        return np.vstack(all_embeddings)
    
    def embed_chunks(self, chunks: List[Dict[str, Any]], show_progress: bool = True) -> List[Dict[str, Any]]:
        """
        Create embeddings for a list of document chunks.

        Args:
            chunks: List of chunks (each with 'text' and 'metadata')
            show_progress: Whether to show a progress bar

        Returns:
            List of chunks with added embeddings
        """
        # Extract texts from chunks
        texts = [chunk["text"] for chunk in chunks]
        
        # Create embeddings
        embeddings = self.embed_texts(texts, show_progress)
        
        # Add embeddings to chunks
        for i, chunk in enumerate(chunks):
            chunk["embedding"] = embeddings[i].tolist()
        
        return chunks 