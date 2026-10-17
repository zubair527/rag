"""Query endpoints for RAG system"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.requests import QueryRequest
from app.schemas.responses import QueryResponse, ErrorResponse
from app.services.rag_service import rag_service
from app.db.session import get_db
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter()


@router.post(
    "/query",
    response_model=QueryResponse,
    responses={500: {"model": ErrorResponse}},
    tags=["Query"],
    summary="Query the RAG system",
    description="Submit a question and get an answer based on indexed documents"
)
async def query_documents(
    request: QueryRequest,
    db: Session = Depends(get_db)
) -> QueryResponse:
    """Query the RAG system with a question"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Execute RAG query
        result = await rag_service.query(
            query=request.query,
            session_id=session_id,
            top_k=request.top_k,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            db=db,
        )

        return QueryResponse(**result)

    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process query: {str(e)}"
        )