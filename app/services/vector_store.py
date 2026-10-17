"""Weaviate vector store service"""
from typing import List, Dict, Any, Optional
import weaviate
from weaviate.classes.config import Configure, Property, DataType
from weaviate.classes.query import MetadataQuery
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class VectorStore:
    """Weaviate vector database interface"""

    def __init__(self):
        self.client: Optional[weaviate.WeaviateClient] = None
        self.collection_name = settings.weaviate_class_name

    def initialize(self) -> None:
        """Initialize Weaviate client and create schema"""
        logger.info(f"Connecting to Weaviate at {settings.weaviate_url}")

        self.client = weaviate.connect_to_custom(
            http_host=settings.weaviate_url.replace("http://", "").replace("https://", ""),
            http_port=8080,
            http_secure=False,
            grpc_host=settings.weaviate_grpc_url.split(":")[0],
            grpc_port=50051,
            grpc_secure=False,
        )

        logger.info("Weaviate client connected successfully")
        self._create_collection()

    def _create_collection(self) -> None:
        """Create Weaviate collection if it doesn't exist"""
        try:
            # Check if collection exists
            if self.client.collections.exists(self.collection_name):
                logger.info(f"Collection '{self.collection_name}' already exists")
                return

            # Create collection with vectorizer configuration
            self.client.collections.create(
                name=self.collection_name,
                properties=[
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="content", data_type=DataType.TEXT),
                    Property(name="chunk_index", data_type=DataType.INT),
                    Property(name="filename", data_type=DataType.TEXT),
                    Property(name="file_type", data_type=DataType.TEXT),
                    Property(name="metadata", data_type=DataType.TEXT),
                ],
                vectorizer_config=Configure.Vectorizer.none(),
                vector_index_config=Configure.VectorIndex.hnsw(
                    distance_metric="cosine"
                ),
            )
            logger.info(f"Collection '{self.collection_name}' created successfully")

        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            raise

    def add_documents(
        self,
        document_id: str,
        texts: List[str],
        embeddings: List[List[float]],
        filename: str,
        file_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """Add document chunks to vector store"""
        if not self.client:
            raise RuntimeError("Vector store not initialized")

        collection = self.client.collections.get(self.collection_name)

        # Prepare objects for batch insertion
        objects = []
        for idx, (text, embedding) in enumerate(zip(texts, embeddings)):
            obj = {
                "document_id": document_id,
                "content": text,
                "chunk_index": idx,
                "filename": filename,
                "file_type": file_type,
                "metadata": str(metadata) if metadata else "",
            }
            objects.append(obj)

        # Batch insert with vectors
        with collection.batch.dynamic() as batch:
            for obj, vector in zip(objects, embeddings):
                batch.add_object(properties=obj, vector=vector)

        logger.info(f"Added {len(objects)} chunks for document {document_id}")
        return len(objects)

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        document_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        if not self.client:
            raise RuntimeError("Vector store not initialized")

        collection = self.client.collections.get(self.collection_name)

        # Build query
        query_builder = collection.query.near_vector(
            near_vector=query_vector,
            limit=top_k,
            return_metadata=MetadataQuery(distance=True)
        )

        # Add filter if document_id is provided
        if document_id:
            query_builder = query_builder.where(
                {"path": ["document_id"], "operator": "Equal", "valueText": document_id}
            )

        # Execute search
        response = query_builder.do()

        # Format results
        results = []
        for obj in response.objects:
            result = {
                "document_id": obj.properties.get("document_id"),
                "content": obj.properties.get("content"),
                "chunk_index": obj.properties.get("chunk_index"),
                "filename": obj.properties.get("filename"),
                "file_type": obj.properties.get("file_type"),
                "distance": obj.metadata.distance if obj.metadata else None,
                "score": 1 - obj.metadata.distance if obj.metadata and obj.metadata.distance else 0,
            }
            results.append(result)

        return results

    def delete_document(self, document_id: str) -> int:
        """Delete all chunks for a document"""
        if not self.client:
            raise RuntimeError("Vector store not initialized")

        collection = self.client.collections.get(self.collection_name)

        # Delete objects matching document_id
        result = collection.data.delete_many(
            where={"path": ["document_id"], "operator": "Equal", "valueText": document_id}
        )

        deleted_count = result.successful if hasattr(result, 'successful') else 0
        logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
        return deleted_count

    def get_document_count(self) -> int:
        """Get total number of document chunks"""
        if not self.client:
            raise RuntimeError("Vector store not initialized")

        collection = self.client.collections.get(self.collection_name)
        response = collection.aggregate.over_all(total_count=True)
        return response.total_count if response.total_count else 0

    def close(self) -> None:
        """Close Weaviate connection"""
        if self.client:
            self.client.close()
            logger.info("Weaviate connection closed")


# Global vector store instance
vector_store = VectorStore()