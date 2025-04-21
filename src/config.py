"""
Configuration settings for the Hermes Ingestor service.
"""

import os
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class QdrantSettings(BaseModel):
    """Settings for Qdrant vector database connection."""
    host: str = os.getenv("QDRANT_HOST", "localhost")
    port: int = int(os.getenv("QDRANT_PORT", "6333"))
    collection_name: str = os.getenv("QDRANT_COLLECTION", "documents")
    prefer_grpc: bool = os.getenv("QDRANT_PREFER_GRPC", "True").lower() == "true"
    api_key: str = os.getenv("QDRANT_API_KEY", "")


class EmbeddingSettings(BaseModel):
    """Settings for embedding model."""
    model_name: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    batch_size: int = int(os.getenv("EMBEDDING_BATCH_SIZE", "32"))
    dimensions: int = int(os.getenv("EMBEDDING_DIMENSIONS", "384"))  # Default for all-MiniLM-L6-v2


class ChunkingSettings(BaseModel):
    """Settings for document chunking."""
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "1000"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "200"))


class AppSettings(BaseModel):
    """Main application settings."""
    app_name: str = "Hermes Ingestor"
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    upload_folder: str = os.getenv("UPLOAD_FOLDER", "uploads")
    supported_formats: list[str] = ["pdf", "txt", "md", "html", "docx"]
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "50"))
    qdrant: QdrantSettings = QdrantSettings()
    embedding: EmbeddingSettings = EmbeddingSettings()
    chunking: ChunkingSettings = ChunkingSettings()


# Global settings instance
settings = AppSettings() 