"""
Authentication middleware for the Hermes Ingestor API.
"""

from fastapi import Security, HTTPException, Depends
from fastapi.security import APIKeyHeader
from ..config import settings
import logging

logger = logging.getLogger(__name__)

api_key_header = APIKeyHeader(name="X-API-Key")

async def get_api_key(api_key: str = Security(api_key_header)):
    """
    Validate the API key from the request header.
    
    Args:
        api_key: The API key from the X-API-Key header
        
    Returns:
        The validated API key
        
    Raises:
        HTTPException: If the API key is invalid
    """
    if api_key != settings.api_key:
        logger.warning(f"Invalid API key attempt from {api_key[:8]}...")
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key 