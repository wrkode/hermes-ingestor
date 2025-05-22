"""
Middleware for the Hermes Ingestor API.
"""

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from ..config import settings
import time
import logging
from typing import Dict, List, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimiter:
    """Rate limiter for API requests."""
    
    def __init__(self):
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.api_key_requests: Dict[str, List[float]] = defaultdict(list)
    
    async def check_rate_limit(self, request: Request) -> Tuple[bool, str]:
        """
        Check if the request should be rate limited.
        
        Args:
            request: The incoming request
            
        Returns:
            Tuple of (is_limited, reason)
        """
        client_ip = request.client.host
        api_key = request.headers.get("X-API-Key", "")
        current_time = time.time()
        
        # Clean old requests
        self._clean_old_requests(client_ip, current_time)
        self._clean_old_requests(api_key, current_time)
        
        # Check IP rate limit
        if len(self.requests[client_ip]) >= settings.rate_limit_requests:
            return True, "Too many requests from this IP"
        
        # Check API key rate limit
        if api_key and len(self.api_key_requests[api_key]) >= settings.rate_limit_requests:
            return True, "Too many requests with this API key"
        
        # Add current request
        self.requests[client_ip].append(current_time)
        if api_key:
            self.api_key_requests[api_key].append(current_time)
        
        return False, ""
    
    def _clean_old_requests(self, key: str, current_time: float):
        """Remove requests older than the rate limit window."""
        window = settings.rate_limit_window
        if key in self.requests:
            self.requests[key] = [t for t in self.requests[key] 
                                if current_time - t < window]
        if key in self.api_key_requests:
            self.api_key_requests[key] = [t for t in self.api_key_requests[key] 
                                        if current_time - t < window]

# Create rate limiter instance
rate_limiter = RateLimiter()

async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware.
    
    Args:
        request: The incoming request
        call_next: The next middleware/route handler
        
    Returns:
        The response from the next handler
    """
    is_limited, reason = await rate_limiter.check_rate_limit(request)
    
    if is_limited:
        logger.warning(f"Rate limit exceeded: {reason}")
        return JSONResponse(
            status_code=429,
            content={"detail": reason}
        )
    
    return await call_next(request) 