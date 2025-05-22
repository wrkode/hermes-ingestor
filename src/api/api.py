"""
Main API module for the Hermes Ingestor.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from .auth import get_api_key
from .middleware import rate_limit_middleware
from ..utils.audit import audit_logger
from ..services.ingestor import IngestorService
from ..config import settings
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hermes Ingestor API",
    description="API for document ingestion and processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add rate limiting middleware
app.middleware("http")(rate_limit_middleware)

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key),
    request: Request = None
):
    """
    Upload a file for processing.
    
    Args:
        file: The file to upload
        api_key: API key for authentication
        request: The incoming request
        
    Returns:
        Dict containing the upload status
    """
    try:
        # Log the upload attempt
        audit_logger.log_event(
            event_type="file_upload",
            user_id=api_key,
            ip_address=request.client.host,
            details={"filename": file.filename}
        )
        
        # Process the file
        ingestor = IngestorService()
        result = await ingestor.process_file(file)
        
        return {
            "status": "success",
            "message": "File uploaded successfully",
            "file_id": result["file_id"]
        }
    except Exception as e:
        logger.error(f"Error processing file: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{file_id}")
async def get_status(
    file_id: str,
    api_key: str = Depends(get_api_key),
    request: Request = None
):
    """
    Get the status of a file processing job.
    
    Args:
        file_id: ID of the file to check
        api_key: API key for authentication
        request: The incoming request
        
    Returns:
        Dict containing the processing status
    """
    try:
        # Log the status check
        audit_logger.log_event(
            event_type="status_check",
            user_id=api_key,
            ip_address=request.client.host,
            details={"file_id": file_id}
        )
        
        ingestor = IngestorService()
        status = await ingestor.get_status(file_id)
        
        return status
    except Exception as e:
        logger.error(f"Error checking status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest-url")
async def ingest_url(
    url: str,
    api_key: str = Depends(get_api_key),
    request: Request = None
):
    """
    Ingest a document from a URL.
    
    Args:
        url: URL of the document to ingest
        api_key: API key for authentication
        request: The incoming request
        
    Returns:
        Dict containing the ingestion status
    """
    try:
        # Log the URL ingestion attempt
        audit_logger.log_event(
            event_type="url_ingest",
            user_id=api_key,
            ip_address=request.client.host,
            details={"url": url}
        )
        
        ingestor = IngestorService()
        result = await ingestor.process_url(url)
        
        return {
            "status": "success",
            "message": "URL ingested successfully",
            "file_id": result["file_id"]
        }
    except Exception as e:
        logger.error(f"Error ingesting URL: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 