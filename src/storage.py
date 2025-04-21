"""
Vector database storage utilities.
"""

from typing import List, Dict, Any, Optional
import uuid
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from qdrant_client.http.exceptions import UnexpectedResponse
import numpy as np
import logging

from .config import settings

logger = logging.getLogger(__name__)


class QdrantStorage:
    """Interface for storing vectors in Qdrant database."""

    def __init__(
        self,
        host: str = None,
        port: int = None,
        collection_name: str = None,
        vector_size: int = None,
        prefer_grpc: bool = None,
        api_key: str = None,
        auto_create_collection: bool = True,
    ):
        """
        Initialize Qdrant storage client.

        Args:
            host: Qdrant server host
            port: Qdrant server port
            collection_name: Name of the collection to use
            vector_size: Size of the vector embeddings
            prefer_grpc: Whether to prefer gRPC over HTTP
            api_key: API key for Qdrant Cloud
            auto_create_collection: Whether to automatically create the collection if it doesn't exist
        """
        # Use settings if not provided
        self.host = host or settings.qdrant.host
        self.port = port or settings.qdrant.port
        self.collection_name = collection_name or settings.qdrant.collection_name
        self.prefer_grpc = prefer_grpc if prefer_grpc is not None else settings.qdrant.prefer_grpc
        self.api_key = api_key or settings.qdrant.api_key
        self.vector_size = vector_size or settings.embedding.dimensions
        
        # Initialize Qdrant client
        if self.api_key:
            # Using Qdrant Cloud
            self.client = QdrantClient(
                url=self.host,
                api_key=self.api_key,
                prefer_grpc=self.prefer_grpc
            )
        else:
            # Using local or custom Qdrant instance
            self.client = QdrantClient(
                host=self.host,
                port=self.port,
                prefer_grpc=self.prefer_grpc
            )
        
        # Auto-create collection if needed
        if auto_create_collection:
            self._ensure_collection_exists()

    def _ensure_collection_exists(self) -> None:
        """
        Ensure that the collection exists, creating it if necessary.
        """
        try:
            collections = self.client.get_collections().collections
            collection_names = [collection.name for collection in collections]
            
            if self.collection_name not in collection_names:
                logger.info(f"Creating Qdrant collection '{self.collection_name}'")
                
                # Create the collection
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(
                        size=self.vector_size,
                        distance=rest.Distance.COSINE
                    )
                )
                
                # Create metadata payload indexes for common fields
                self._create_payload_indexes()
                
                logger.info(f"Successfully created collection '{self.collection_name}'")
        except Exception as e:
            logger.error(f"Error checking/creating collection: {str(e)}")
            raise

    def _create_payload_indexes(self) -> None:
        """
        Create payload indexes for faster filtering.
        """
        # List of fields to index
        index_fields = [
            ("filename", "keyword"),
            ("file_type", "keyword"),
            ("title", "text"),
            ("author", "keyword"),
            ("chunk_id", "integer"),
            ("location", "keyword"),
        ]
        
        for field_name, field_type in index_fields:
            try:
                field_schema = None
                
                # Define the schema based on field type
                if field_type == "keyword":
                    field_schema = rest.PayloadSchemaType.KEYWORD
                elif field_type == "integer":
                    field_schema = rest.PayloadSchemaType.INTEGER
                elif field_type == "text":
                    field_schema = rest.PayloadSchemaType.TEXT
                
                if field_schema:
                    # Create the index
                    self.client.create_payload_index(
                        collection_name=self.collection_name,
                        field_name=f"metadata.{field_name}",
                        field_schema=field_schema
                    )
            except UnexpectedResponse:
                # Index might already exist, which is fine
                pass
            except Exception as e:
                logger.warning(f"Failed to create index for {field_name}: {str(e)}")

    def store_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Store document chunks in Qdrant.

        Args:
            chunks: List of chunks with text, metadata, and embeddings

        Returns:
            List of IDs assigned to the stored chunks
        """
        if not chunks:
            return []
        
        # Prepare points for Qdrant
        points = []
        ids = []
        
        for chunk in chunks:
            # Generate a unique ID for the chunk
            chunk_id = str(uuid.uuid4())
            ids.append(chunk_id)
            
            # Create a Qdrant point
            points.append(
                rest.PointStruct(
                    id=chunk_id,
                    vector=chunk["embedding"],
                    payload={
                        "text": chunk["text"],
                        "metadata": chunk["metadata"]
                    }
                )
            )
        
        # Upsert points to Qdrant
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        
        return ids
    
    def search(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors in Qdrant.

        Args:
            query_vector: The query vector to search for
            limit: Maximum number of results to return
            filters: Optional filters to apply to the search

        Returns:
            List of matching documents
        """
        # Prepare filter conditions if any
        filter_conditions = None
        if filters:
            conditions = []
            for key, value in filters.items():
                if isinstance(value, (list, tuple)):
                    # For lists, create a should condition (OR)
                    or_conditions = [
                        rest.FieldCondition(
                            key=f"metadata.{key}",
                            match=rest.MatchValue(value=v)
                        )
                        for v in value
                    ]
                    conditions.append(rest.Filter(should=or_conditions))
                else:
                    # For single values, create a must condition (AND)
                    conditions.append(
                        rest.FieldCondition(
                            key=f"metadata.{key}",
                            match=rest.MatchValue(value=value)
                        )
                    )
            
            # Combine all conditions with AND
            filter_conditions = rest.Filter(
                must=conditions
            )
        
        # Execute the search
        search_results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            query_filter=filter_conditions,
            with_payload=True,
            with_vectors=False
        )
        
        # Format the results
        results = []
        for hit in search_results:
            results.append({
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload.get("text", ""),
                "metadata": hit.payload.get("metadata", {})
            })
        
        return results
    
    def delete_by_filters(self, filters: Dict[str, Any]) -> int:
        """
        Delete vectors matching the given filters.

        Args:
            filters: Filters to match for deletion

        Returns:
            Number of deleted vectors
        """
        # Prepare filter conditions
        conditions = []
        for key, value in filters.items():
            if isinstance(value, (list, tuple)):
                or_conditions = [
                    rest.FieldCondition(
                        key=f"metadata.{key}",
                        match=rest.MatchValue(value=v)
                    )
                    for v in value
                ]
                conditions.append(rest.Filter(should=or_conditions))
            else:
                conditions.append(
                    rest.FieldCondition(
                        key=f"metadata.{key}",
                        match=rest.MatchValue(value=value)
                    )
                )
        
        # Combine all conditions with AND
        filter_conditions = rest.Filter(
            must=conditions
        )
        
        # Execute the deletion
        result = self.client.delete(
            collection_name=self.collection_name,
            points_selector=rest.FilterSelector(
                filter=filter_conditions
            )
        )
        
        # Return the number of deleted points
        return result.operation_id
    
    def count_by_filters(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Count vectors matching the given filters.

        Args:
            filters: Optional filters to match for counting

        Returns:
            Number of matching vectors
        """
        if not filters:
            # Count all vectors
            return self.client.count(
                collection_name=self.collection_name
            ).count
        
        # Prepare filter conditions
        conditions = []
        for key, value in filters.items():
            if isinstance(value, (list, tuple)):
                or_conditions = [
                    rest.FieldCondition(
                        key=f"metadata.{key}",
                        match=rest.MatchValue(value=v)
                    )
                    for v in value
                ]
                conditions.append(rest.Filter(should=or_conditions))
            else:
                conditions.append(
                    rest.FieldCondition(
                        key=f"metadata.{key}",
                        match=rest.MatchValue(value=value)
                    )
                )
        
        # Combine all conditions with AND
        filter_conditions = rest.Filter(
            must=conditions
        )
        
        # Execute the count
        return self.client.count(
            collection_name=self.collection_name,
            count_filter=filter_conditions
        ).count 