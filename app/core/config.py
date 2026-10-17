"""Configuration management using Pydantic Settings"""
from functools import lru_cache
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # Application
    app_name: str = Field(default="production-rag-system")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="production")

    # FastAPI
    fastapi_host: str = Field(default="0.0.0.0")
    fastapi_port: int = Field(default=8000)
    api_v1_prefix: str = Field(default="/api/v1")

    # Ollama
    ollama_base_url: str = Field(default="http://ollama:11434")
    ollama_model: str = Field(default="llama3.2:1b")
    ollama_temperature: float = Field(default=0.7)
    ollama_max_tokens: int = Field(default=2048)

    # Weaviate
    weaviate_url: str = Field(default="http://weaviate:8080")
    weaviate_grpc_url: str = Field(default="weaviate:50051")
    weaviate_class_name: str = Field(default="Documents")

    # Embeddings
    embedding_model_name: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_dimension: int = Field(default=384)
    embedding_batch_size: int = Field(default=32)

    # Redis
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)
    redis_cache_ttl: int = Field(default=3600)

    # MariaDB
    mariadb_host: str = Field(default="mariadb")
    mariadb_port: int = Field(default=3306)
    mariadb_database: str = Field(default="rag_metadata")
    mariadb_user: str = Field(default="rag_user")
    mariadb_password: str = Field(default="rag_password")
    mariadb_root_password: str = Field(default="root_password")

    # Document Processing
    max_upload_size: int = Field(default=52428800)  # 50MB
    chunk_size: int = Field(default=1000)
    chunk_overlap: int = Field(default=200)

    # Logging
    log_level: str = Field(default="INFO")

    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy database URL"""
        return (
            f"mysql+pymysql://{self.mariadb_user}:{self.mariadb_password}"
            f"@{self.mariadb_host}:{self.mariadb_port}/{self.mariadb_database}"
        )

    @property
    def redis_url(self) -> str:
        """Generate Redis URL"""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()
