"""
Main entry point for the Hermes Ingestor service.
"""

import uvicorn
import os
import argparse
import logging

from .api.app import app
from .config import settings


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Hermes Ingestor service")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to listen on")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()


def main():
    """Run the Hermes Ingestor service."""
    # Parse command line arguments
    args = parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.debug or settings.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Log startup message
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Hermes Ingestor service on {args.host}:{args.port}")
    
    # Create upload directory if it doesn't exist
    os.makedirs(settings.upload_folder, exist_ok=True)
    
    # Run the service
    uvicorn.run(
        "src.api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="debug" if args.debug or settings.debug else "info"
    )


if __name__ == "__main__":
    main() 