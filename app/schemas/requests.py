"""Request schemas using Pydantic"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, field_validator


class QueryRequest(BaseModel):
    """Query request schema"""
    query: str = Field(..., min_length=1, max_length=2000, description="User query")
    session_id: Optional[str] = Field(None, description="Session ID for chat history")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to retrieve")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: Optional[int] = Field(default=2048, ge=100, le=4096, description="Max tokens to generate")

    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and clean query"""
        return v.strip()


class DocumentUploadMetadata(BaseModel):
    """Document upload metadata"""
    tags: Optional[List[str]] = Field(default=None, description="Document tags")
    source: Optional[str] = Field(default=None, description="Document source")
    author: Optional[str] = Field(default=None, description="Document author")
    custom_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Custom metadata")


class TextDocumentRequest(BaseModel):
    """Text document ingestion request"""
    content: str = Field(..., min_length=1, description="Document content")
    filename: str = Field(..., min_length=1, max_length=512, description="Document filename")
    metadata: Optional[DocumentUploadMetadata] = Field(default=None, description="Document metadata")


class DeleteDocumentRequest(BaseModel):
    """Delete document request"""
    document_id: str = Field(..., description="Document ID to delete")