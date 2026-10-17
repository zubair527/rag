"""RAG orchestration service"""
import time
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.logging import get_logger
from app.services.embedding_service import embedding_service
from app.services.vector_store import vector_store
from app.services.llm_service import llm_service
from app.models.database import ChatHistory, QueryMetrics

logger = get_logger(__name__)


class RAGService:
    """RAG orchestration service combining all components"""

    async def query(
        self,
        query: str,
        session_id: str,
        top_k: int = 5,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        db: Optional[Session] = None,
    ) -> Dict[str, Any]:
        """Execute RAG query pipeline"""
        start_time = time.time()
        metrics = {}

        try:
            # Step 1: Generate query embedding
            embed_start = time.time()
            query_embedding = embedding_service.embed_text(query)
            metrics["embedding_time"] = time.time() - embed_start
            logger.info(f"Query embedding generated in {metrics['embedding_time']:.3f}s")

            # Step 2: Search vector database
            search_start = time.time()
            search_results = vector_store.search(
                query_vector=query_embedding,
                top_k=top_k
            )
            metrics["search_time"] = time.time() - search_start
            metrics["results_count"] = len(search_results)
            logger.info(f"Vector search completed in {metrics['search_time']:.3f}s, found {len(search_results)} results")

            # Step 3: Format context and generate answer
            llm_start = time.time()
            context = llm_service.format_context(search_results)

            if not context.strip():
                answer = "I don't have any relevant information to answer this question. Please upload some documents first."
            else:
                answer = llm_service.generate_answer(
                    question=query,
                    context=context,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )

            metrics["llm_time"] = time.time() - llm_start
            logger.info(f"Answer generated in {metrics['llm_time']:.3f}s")

            # Calculate total time
            total_time = time.time() - start_time
            metrics["total_time"] = total_time

            # Prepare response
            response = {
                "answer": answer,
                "sources": search_results,
                "session_id": session_id,
                "response_time": total_time,
                "model_used": llm_service.get_model_name(),
            }

            # Save to database if available
            if db:
                self._save_chat_history(
                    db=db,
                    session_id=session_id,
                    user_message=query,
                    assistant_message=answer,
                    context_documents=search_results,
                    response_time=total_time,
                )
                self._save_query_metrics(db=db, query=query, metrics=metrics)

            return response

        except Exception as e:
            logger.error(f"Error in RAG query pipeline: {e}")
            raise

    def _save_chat_history(
        self,
        db: Session,
        session_id: str,
        user_message: str,
        assistant_message: str,
        context_documents: list,
        response_time: float,
    ) -> None:
        """Save chat interaction to database"""
        try:
            chat_record = ChatHistory(
                session_id=session_id,
                user_message=user_message,
                assistant_message=assistant_message,
                context_documents=[
                    {
                        "document_id": doc.get("document_id"),
                        "filename": doc.get("filename"),
                        "chunk_index": doc.get("chunk_index"),
                        "score": doc.get("score"),
                    }
                    for doc in context_documents
                ],
                response_time=response_time,
            )
            db.add(chat_record)
            db.commit()
            logger.debug("Chat history saved")
        except Exception as e:
            logger.error(f"Error saving chat history: {e}")
            db.rollback()

    def _save_query_metrics(
        self,
        db: Session,
        query: str,
        metrics: Dict[str, Any],
    ) -> None:
        """Save query metrics to database"""
        try:
            metric_record = QueryMetrics(
                query=query,
                embedding_time=metrics.get("embedding_time"),
                search_time=metrics.get("search_time"),
                llm_time=metrics.get("llm_time"),
                total_time=metrics.get("total_time"),
                results_count=metrics.get("results_count"),
            )
            db.add(metric_record)
            db.commit()
            logger.debug("Query metrics saved")
        except Exception as e:
            logger.error(f"Error saving query metrics: {e}")
            db.rollback()


# Global RAG service instance
rag_service = RAGService()
