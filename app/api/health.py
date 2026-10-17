"""Health check endpoints"""
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.responses import HealthResponse
from app.core.config import get_settings
from app.db.session import get_db
from app.services.vector_store import vector_store
from app.core.logging import get_logger
import redis

logger = get_logger(__name__)
settings = get_settings()
router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check(db: Session = Depends(get_db)) -> HealthResponse:
    """Check health status of all services"""
    services = {}

    # Check database
    try:
        db.execute("SELECT 1")
        services["database"] = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        services["database"] = "unhealthy"

    # Check Redis
    try:
        redis_client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        redis_client.ping()
        services["redis"] = "healthy"
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        services["redis"] = "unhealthy"

    # Check Weaviate
    try:
        if vector_store.client and vector_store.client.is_ready():
            services["weaviate"] = "healthy"
        else:
            services["weaviate"] = "unhealthy"
    except Exception as e:
        logger.error(f"Weaviate health check failed: {e}")
        services["weaviate"] = "unhealthy"

    # Check Ollama
    try:
        import httpx
        response = httpx.get(f"{settings.ollama_base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            services["ollama"] = "healthy"
        else:
            services["ollama"] = "unhealthy"
    except Exception as e:
        logger.error(f"Ollama health check failed: {e}")
        services["ollama"] = "unhealthy"

    # Overall status
    status = "healthy" if all(s == "healthy" for s in services.values()) else "degraded"

    return HealthResponse(
        status=status,
        version=settings.app_version,
        timestamp=datetime.utcnow(),
        services=services,
    )