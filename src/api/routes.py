"""
API routes for Hermes Ingestor service.
"""

import os
from typing import List, Dict, Any, Optional
import logging
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, BackgroundTasks
from fastapi.responses import JSONResponse
import json

from ..ingestor import Ingestor
from ..storage import QdrantStorage
from ..config import settings
from . import models
from .. import __version__

# Set up logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()

# Initialize services
ingestor = Ingestor()
storage = QdrantStorage()


def _parse_metadata(metadata_str: str = Form(None)) -> Optional[Dict[str, Any]]:
    """
    Parse metadata JSON string.
    
    Args:
        metadata_str: JSON string of metadata or None
        
    Returns:
        Parsed metadata dict or None
    """
    if not metadata_str:
        return None
    
    try:
        return json.loads(metadata_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid metadata JSON format")


@router.post(
    "/ingest/file",
    response_model=models.ProcessingResponse,
    summary="Ingest a single document",
    description="Upload and process a single document file"
)
async def ingest_file(
    file: UploadFile = File(...),
    metadata: Optional[Dict[str, Any]] = Depends(_parse_metadata)
):
    """
    Ingest a single document file.
    
    Args:
        file: The document file to process
        metadata: Optional metadata to include with the document
        
    Returns:
        Processing result
    """
    # Check file extension
    _, ext = os.path.splitext(file.filename)
    ext = ext[1:].lower() if ext else ""
    
    if ext not in settings.supported_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format: {ext}. Supported formats: {', '.join(settings.supported_formats)}"
        )
    
    # Check file size
    if file.size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
        )
    
    try:
        # Read the file content first
        file_content = await file.read()
        
        # Process the file without awaiting the process_upload function
        result = ingestor.process_upload(file_content, file.filename, metadata)
        
        # Create response
        response = models.ProcessingResponse(
            success=result["success"],
            file_name=result["file_name"],
            chunks_created=result.get("chunks_created"),
            processing_time=result.get("processing_time"),
            error=result.get("error")
        )
        
        return response
    
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post(
    "/ingest/files",
    response_model=models.BatchProcessingResponse,
    summary="Ingest multiple documents",
    description="Upload and process multiple document files"
)
async def ingest_files(
    files: List[UploadFile] = File(...),
    metadata: Optional[Dict[str, Any]] = Depends(_parse_metadata),
    background_tasks: BackgroundTasks = None
):
    """
    Ingest multiple document files.
    
    Args:
        files: List of document files to process
        metadata: Optional metadata to include with all documents
        background_tasks: FastAPI background tasks
        
    Returns:
        Batch processing result
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    results = []
    successful = 0
    failed = 0
    
    for file in files:
        # Check file extension
        _, ext = os.path.splitext(file.filename)
        ext = ext[1:].lower() if ext else ""
        
        if ext not in settings.supported_formats:
            # Skip unsupported files
            results.append(models.ProcessingResponse(
                success=False,
                file_name=file.filename,
                error=f"Unsupported file format: {ext}"
            ))
            failed += 1
            continue
        
        # Check file size
        if file.size > settings.max_file_size_mb * 1024 * 1024:
            results.append(models.ProcessingResponse(
                success=False,
                file_name=file.filename,
                error=f"File too large. Maximum size: {settings.max_file_size_mb}MB"
            ))
            failed += 1
            continue
        
        try:
            # Read the file content first
            file_content = await file.read()
            
            # Process the file without awaiting the process_upload function
            result = ingestor.process_upload(file_content, file.filename, metadata)
            
            # Create response
            response = models.ProcessingResponse(
                success=result["success"],
                file_name=result["file_name"],
                chunks_created=result.get("chunks_created"),
                processing_time=result.get("processing_time"),
                error=result.get("error")
            )
            
            results.append(response)
            
            if result["success"]:
                successful += 1
            else:
                failed += 1
        
        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}", exc_info=True)
            results.append(models.ProcessingResponse(
                success=False,
                file_name=file.filename,
                error=f"Error processing file: {str(e)}"
            ))
            failed += 1
    
    # Create batch response
    return models.BatchProcessingResponse(
        total_files=len(files),
        successful=successful,
        failed=failed,
        results=results
    )


@router.delete(
    "/document/{filename}",
    response_model=models.DeleteResponse,
    summary="Delete a document",
    description="Delete a document and its chunks by filename"
)
async def delete_document(filename: str):
    """
    Delete a document and all its chunks.
    
    Args:
        filename: Name of the file to delete
        
    Returns:
        Deletion result
    """
    try:
        # Delete the document
        result = ingestor.delete_document(filename)
        
        # Create response
        return models.DeleteResponse(
            success=result["success"],
            deleted_count=result["deleted_count"],
            error=result.get("error")
        )
    
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")


@router.post(
    "/document/delete",
    response_model=models.DeleteResponse,
    summary="Delete documents by filter",
    description="Delete documents and their chunks by metadata filter"
)
async def delete_documents_by_filter(filters: Dict[str, Any]):
    """
    Delete documents and their chunks by metadata filter.
    
    Args:
        filters: Metadata filters to match documents for deletion
        
    Returns:
        Deletion result
    """
    try:
        # Delete the documents
        result = ingestor.delete_document(filters)
        
        # Create response
        return models.DeleteResponse(
            success=result["success"],
            deleted_count=result["deleted_count"],
            error=result.get("error")
        )
    
    except Exception as e:
        logger.error(f"Error deleting documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting documents: {str(e)}")


@router.get(
    "/health",
    response_model=models.HealthResponse,
    summary="Health check",
    description="Check the health of the service"
)
async def health_check():
    """
    Check the health of the service.
    
    Returns:
        Health status
    """
    # Check Qdrant connection
    qdrant_status = "healthy"
    try:
        storage.client.get_collections()
    except Exception as e:
        logger.error(f"Qdrant health check failed: {str(e)}")
        qdrant_status = f"unhealthy: {str(e)}"
    
    return models.HealthResponse(
        status="healthy",
        version=__version__,
        qdrant_status=qdrant_status
    )


@router.get(
    "/status",
    response_model=models.StatusResponse,
    summary="Service status",
    description="Get the status of the service"
)
async def service_status():
    """
    Get the status of the service.
    
    Returns:
        Service status
    """
    try:
        # Get unique document count by using a specialized filter query
        # instead of the unsupported group_by parameter
        try:
            # Get all documents with payload that contains filename metadata
            results = storage.client.scroll(
                collection_name=settings.qdrant.collection_name,
                scroll_filter=None,
                limit=1000,  # Set a reasonable limit
                with_payload=True,
                with_vectors=False
            )
            
            # Extract unique filenames manually
            unique_filenames = set()
            for point in results[0]:
                if point.payload and "metadata" in point.payload and "filename" in point.payload["metadata"]:
                    unique_filenames.add(point.payload["metadata"]["filename"])
            
            document_count = len(unique_filenames)
        except Exception as e:
            logger.warning(f"Error getting unique document count: {str(e)}")
            document_count = 0
        
        # Get chunk count
        chunk_count = storage.count_by_filters()
        
        # Get storage usage
        storage_usage = {
            "documents": document_count,
            "chunks": chunk_count,
        }
        
        return models.StatusResponse(
            status="running",
            document_count=document_count,
            chunk_count=chunk_count,
            storage_usage=storage_usage
        )
    
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting service status: {str(e)}") 