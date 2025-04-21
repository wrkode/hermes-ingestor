"""
Document ingestion pipeline.
"""

import os
import logging
import time
from typing import List, Dict, Any, Optional, Union
import shutil
import tempfile

from .processors.factory import get_processor
from .chunker import create_chunks
from .embedder import Embedder
from .storage import QdrantStorage
from .config import settings

logger = logging.getLogger(__name__)


class Ingestor:
    """Main document ingestion pipeline."""

    def __init__(self):
        """Initialize the ingestor with default components."""
        self.embedder = Embedder()
        self.storage = QdrantStorage()
        self.upload_dir = settings.upload_folder
        
        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def process_file(
        self,
        file_path: str,
        metadata: Optional[Dict[str, Any]] = None,
        delete_after: bool = False
    ) -> Dict[str, Any]:
        """
        Process a single document file through the ingestion pipeline.

        Args:
            file_path: Path to the document file
            metadata: Additional metadata to include with the document
            delete_after: Whether to delete the file after processing

        Returns:
            Dict with processing results including number of chunks created
        """
        start_time = time.time()
        
        try:
            # Get the appropriate processor for the file
            processor = get_processor(file_path)
            if not processor:
                raise ValueError(f"Unsupported file type: {file_path}")
            
            # Extract text and metadata from the document
            logger.info(f"Extracting text from {file_path}")
            document_text = processor.extract_text()
            
            # Extract metadata
            document_metadata = processor.extract_metadata()
            
            # Add additional metadata if provided
            if metadata:
                document_metadata.update(metadata)
            
            # Add ingestion timestamp
            document_metadata["ingested_at"] = time.time()
            
            # Create chunks from the document
            logger.info(f"Chunking document: {file_path}")
            chunks = create_chunks(document_text, document_metadata)
            
            # Create embeddings for the chunks
            logger.info(f"Creating embeddings for {len(chunks)} chunks")
            embedded_chunks = self.embedder.embed_chunks(chunks)
            
            # Store chunks in the vector database
            logger.info(f"Storing {len(embedded_chunks)} chunks in Qdrant")
            chunk_ids = self.storage.store_chunks(embedded_chunks)
            
            # Clean up if requested
            if delete_after and os.path.exists(file_path):
                logger.info(f"Deleting processed file: {file_path}")
                os.remove(file_path)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            
            # Return results
            return {
                "success": True,
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "chunks_created": len(chunks),
                "processing_time": processing_time,
                "chunk_ids": chunk_ids
            }
        
        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}", exc_info=True)
            return {
                "success": False,
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "error": str(e)
            }
    
    def process_upload(
        self,
        file_obj: Any,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process an uploaded file.

        Args:
            file_obj: The file object (bytes or file-like object)
            filename: Name of the file
            metadata: Additional metadata to include

        Returns:
            Dict with processing results
        """
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
            # Write the file content - handle both bytes and file-like objects
            if isinstance(file_obj, bytes):
                # If it's already bytes, just write it
                tmp.write(file_obj)
            else:
                # If it's a file-like object, use copyfileobj
                shutil.copyfileobj(file_obj, tmp)
            tmp_path = tmp.name
        
        try:
            # Process the temporary file
            result = self.process_file(tmp_path, metadata, delete_after=True)
            return result
        except Exception as e:
            # Clean up the temporary file in case of error
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
            raise e
    
    def process_files(
        self,
        file_paths: List[str],
        metadata: Optional[Dict[str, Any]] = None,
        delete_after: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Process multiple document files.

        Args:
            file_paths: List of paths to document files
            metadata: Additional metadata to include with all documents
            delete_after: Whether to delete files after processing

        Returns:
            List of dicts with processing results for each file
        """
        results = []
        
        for file_path in file_paths:
            result = self.process_file(file_path, metadata, delete_after)
            results.append(result)
        
        return results
    
    def process_directory(
        self,
        directory_path: str,
        recursive: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        delete_after: bool = False,
        extensions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Process all supported documents in a directory.

        Args:
            directory_path: Path to the directory containing documents
            recursive: Whether to process subdirectories recursively
            metadata: Additional metadata to include with all documents
            delete_after: Whether to delete files after processing
            extensions: List of file extensions to process (if None, use supported formats from config)

        Returns:
            List of dicts with processing results for each file
        """
        if not os.path.isdir(directory_path):
            raise ValueError(f"Not a directory: {directory_path}")
        
        file_paths = []
        supported_extensions = extensions or settings.supported_formats
        
        # Normalize extensions to lowercase with dot
        supported_extensions = [f".{ext.lower().lstrip('.')}" for ext in supported_extensions]
        
        # Walk through the directory (recursively if requested)
        if recursive:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    _, ext = os.path.splitext(file_path.lower())
                    if ext in supported_extensions:
                        file_paths.append(file_path)
        else:
            for file in os.listdir(directory_path):
                file_path = os.path.join(directory_path, file)
                if os.path.isfile(file_path):
                    _, ext = os.path.splitext(file_path.lower())
                    if ext in supported_extensions:
                        file_paths.append(file_path)
        
        # Process all found files
        return self.process_files(file_paths, metadata, delete_after)
    
    def delete_document(self, document_identifier: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Delete a document and all its chunks from the vector database.

        Args:
            document_identifier: Either a filename or a dict of metadata filters

        Returns:
            Dict with deletion results
        """
        try:
            # Prepare filters
            if isinstance(document_identifier, str):
                # Assume it's a filename
                filters = {"filename": document_identifier}
            else:
                # It's a metadata filter dict
                filters = document_identifier
            
            # Count matching documents before deletion
            before_count = self.storage.count_by_filters(filters)
            
            if before_count == 0:
                return {
                    "success": False,
                    "error": "No documents match the given identifier",
                    "deleted_count": 0
                }
            
            # Delete matching documents
            operation_id = self.storage.delete_by_filters(filters)
            
            return {
                "success": True,
                "deleted_count": before_count,
                "operation_id": operation_id,
                "filters": filters
            }
        
        except Exception as e:
            logger.error(f"Error deleting document: {str(e)}", exc_info=True)
            return {
                "success": False,
                "error": str(e),
                "deleted_count": 0
            } 