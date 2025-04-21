"""
Pydantic models for the API.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    
    source: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    category: Optional[str] = None
    custom_metadata: Optional[Dict[str, Any]] = None


class ProcessingResponse(BaseModel):
    """Response model for document processing."""
    
    success: bool = Field(..., description="Whether the processing was successful")
    file_name: str = Field(..., description="Name of the processed file")
    chunks_created: Optional[int] = Field(None, description="Number of chunks created")
    processing_time: Optional[float] = Field(None, description="Processing time in seconds")
    error: Optional[str] = Field(None, description="Error message if processing failed")


class BatchProcessingResponse(BaseModel):
    """Response model for batch document processing."""
    
    total_files: int = Field(..., description="Total number of files processed")
    successful: int = Field(..., description="Number of files successfully processed")
    failed: int = Field(..., description="Number of files that failed processing")
    results: List[ProcessingResponse] = Field(..., description="Individual processing results")


class DeleteResponse(BaseModel):
    """Response model for document deletion."""
    
    success: bool = Field(..., description="Whether the deletion was successful")
    deleted_count: int = Field(..., description="Number of chunks deleted")
    error: Optional[str] = Field(None, description="Error message if deletion failed")


class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Service version")
    qdrant_status: str = Field(..., description="Qdrant connection status")


class StatusResponse(BaseModel):
    """Response model for service status."""
    
    status: str = Field(..., description="Service status")
    document_count: int = Field(..., description="Total number of documents in the database")
    chunk_count: int = Field(..., description="Total number of chunks in the database")
    storage_usage: Dict[str, Any] = Field(..., description="Storage usage information") 