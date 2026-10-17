"""Response schemas using Pydantic"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Current timestamp")
    services: Dict[str, str] = Field(..., description="Service statuses")


class QueryResponse(BaseModel):
    """Query response schema"""
    answer: str = Field(..., description="Generated answer")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents")
    session_id: str = Field(..., description="Session ID")
    response_time: float = Field(..., description="Response time in seconds")
    model_used: str = Field(..., description="Model used for generation")


class DocumentUploadResponse(BaseModel):
    """Document upload response"""
    document_id: str = Field(..., description="Unique document ID")
    filename: str = Field(..., description="Document filename")
    chunk_count: int = Field(..., description="Number of chunks created")
    file_size: int = Field(..., description="File size in bytes")
    status: str = Field(..., description="Upload status")
    message: str = Field(..., description="Status message")


class DocumentListResponse(BaseModel):
    """Document list response"""
    documents: List[Dict[str, Any]] = Field(..., description="List of documents")
    total: int = Field(..., description="Total number of documents")


class DocumentDeleteResponse(BaseModel):
    """Document delete response"""
    document_id: str = Field(..., description="Deleted document ID")
    status: str = Field(..., description="Delete status")
    message: str = Field(..., description="Status message")


class ErrorResponse(BaseModel):
    """Error response"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Error details")