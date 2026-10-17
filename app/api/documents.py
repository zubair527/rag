"""Document management endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import json
from app.schemas.requests import TextDocumentRequest, DeleteDocumentRequest, DocumentUploadMetadata
from app.schemas.responses import (
    DocumentUploadResponse,
    DocumentListResponse,
    DocumentDeleteResponse,
    ErrorResponse,
)
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.document_processor import document_processor
from app.models.database import Document
from app.db.session import get_db
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()


@router.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Documents"],
    summary="Upload a document file",
    description="Upload PDF or text file for indexing"
)
async def upload_document(
    file: UploadFile = File(..., description="Document file to upload"),
    metadata: str = Form(None, description="JSON string of document metadata"),
    db: Session = Depends(get_db)
) -> DocumentUploadResponse:
    """Upload and process a document file"""
    try:
        # Validate file type
        allowed_types = ["application/pdf", "text/plain"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Allowed types: PDF, TXT"
            )

        # Validate file size
        content = await file.read()
        file_size = len(content)
        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum allowed size of {settings.max_upload_size} bytes"
            )

        await file.seek(0)  # Reset file pointer

        # Extract text based on file type
        if file.content_type == "application/pdf":
            text = document_processor.extract_text_from_pdf(file.file)
            file_type = "pdf"
        else:
            text = document_processor.extract_text_from_txt(file.file)
            file_type = "txt"

        if not text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the document"
            )

        # Parse metadata if provided
        doc_metadata = None
        if metadata:
            try:
                doc_metadata = json.loads(metadata)
            except json.JSONDecodeError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid JSON metadata"
                )

        # Process document
        processed = document_processor.process_document(
            content=text,
            filename=file.filename,
            file_type=file_type,
        )

        # Generate embeddings for chunks
        embeddings = embedding_service.embed_texts(processed["chunks"])

        # Store in vector database
        vector_store.add_documents(
            document_id=processed["document_id"],
            texts=processed["chunks"],
            embeddings=embeddings,
            filename=file.filename,
            file_type=file_type,
            metadata=doc_metadata,
        )

        # Save metadata to database
        db_document = Document(
            document_id=processed["document_id"],
            filename=file.filename,
            file_type=file_type,
            file_size=file_size,
            content_hash=processed["content_hash"],
            chunk_count=processed["chunk_count"],
            metadata=doc_metadata,
        )
        db.add(db_document)
        db.commit()

        logger.info(f"Document uploaded successfully: {file.filename} ({processed['chunk_count']} chunks)")

        return DocumentUploadResponse(
            document_id=processed["document_id"],
            filename=file.filename,
            chunk_count=processed["chunk_count"],
            file_size=file_size,
            status="success",
            message="Document uploaded and indexed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload document: {str(e)}"
        )


@router.post(
    "/documents/text",
    response_model=DocumentUploadResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Documents"],
    summary="Add text document",
    description="Add text content directly for indexing"
)
async def add_text_document(
    request: TextDocumentRequest,
    db: Session = Depends(get_db)
) -> DocumentUploadResponse:
    """Add text document directly"""
    try:
        if not request.content.strip():
            raise HTTPException(
                status_code=400,
                detail="Document content cannot be empty"
            )

        # Process document
        processed = document_processor.process_document(
            content=request.content,
            filename=request.filename,
            file_type="text",
        )

        # Generate embeddings
        embeddings = embedding_service.embed_texts(processed["chunks"])

        # Store in vector database
        metadata_dict = request.metadata.model_dump() if request.metadata else None
        vector_store.add_documents(
            document_id=processed["document_id"],
            texts=processed["chunks"],
            embeddings=embeddings,
            filename=request.filename,
            file_type="text",
            metadata=metadata_dict,
        )

        # Save to database
        file_size = len(request.content.encode('utf-8'))
        db_document = Document(
            document_id=processed["document_id"],
            filename=request.filename,
            file_type="text",
            file_size=file_size,
            content_hash=processed["content_hash"],
            chunk_count=processed["chunk_count"],
            metadata=metadata_dict,
        )
        db.add(db_document)
        db.commit()

        logger.info(f"Text document added: {request.filename} ({processed['chunk_count']} chunks)")

        return DocumentUploadResponse(
            document_id=processed["document_id"],
            filename=request.filename,
            chunk_count=processed["chunk_count"],
            file_size=file_size,
            status="success",
            message="Text document indexed successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding text document: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add text document: {str(e)}"
        )


@router.get(
    "/documents",
    response_model=DocumentListResponse,
    tags=["Documents"],
    summary="List all documents",
    description="Get list of all indexed documents"
)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> DocumentListResponse:
    """List all documents"""
    try:
        documents = db.query(Document).offset(skip).limit(limit).all()
        total = db.query(Document).count()

        doc_list = [
            {
                "document_id": doc.document_id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "chunk_count": doc.chunk_count,
                "created_at": doc.created_at.isoformat(),
                "metadata": doc.metadata,
            }
            for doc in documents
        ]

        return DocumentListResponse(documents=doc_list, total=total)

    except Exception as e:
        logger.error(f"Error listing documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list documents: {str(e)}"
        )


@router.delete(
    "/documents/{document_id}",
    response_model=DocumentDeleteResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Documents"],
    summary="Delete a document",
    description="Delete a document and all its chunks"
)
async def delete_document(
    document_id: str,
    db: Session = Depends(get_db)
) -> DocumentDeleteResponse:
    """Delete a document"""
    try:
        # Check if document exists
        db_document = db.query(Document).filter(Document.document_id == document_id).first()
        if not db_document:
            raise HTTPException(
                status_code=404,
                detail=f"Document not found: {document_id}"
            )

        # Delete from vector store
        vector_store.delete_document(document_id)

        # Delete from database
        db.delete(db_document)
        db.commit()

        logger.info(f"Document deleted: {document_id}")

        return DocumentDeleteResponse(
            document_id=document_id,
            status="success",
            message="Document deleted successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete document: {str(e)}"
        )