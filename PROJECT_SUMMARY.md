# RAG - Project Summary

## Overview

A complete, production-grade Retrieval-Augmented Generation (RAG) system that runs entirely locally using Docker containers. Built following the architecture diagram provided.

## What's Included

### Core Application
- ✅ **FastAPI Application** - RESTful API with full CRUD operations
- ✅ **LangChain Integration** - Orchestration layer with prompt templates and chain management
- ✅ **Document Processing** - PDF and text file ingestion with chunking
- ✅ **Embedding Service** - sentence-transformers (all-MiniLM-L6-v2) with Redis caching
- ✅ **Vector Database** - Weaviate for semantic search
- ✅ **LLM Service** - Ollama with llama3.2:1b (smallest model, ~700MB)

### Infrastructure Services
- ✅ **Nginx** - API Gateway with rate limiting and load balancing
- ✅ **MariaDB** - Metadata storage and chat history persistence
- ✅ **Redis** - Caching layer for embeddings and responses
- ✅ **Prometheus** - Monitoring and metrics collection

### User Interfaces
- ✅ **Streamlit UI** - Interactive web interface for document upload and chat
- ✅ **Swagger/OpenAPI** - Auto-generated API documentation
- ✅ **ReDoc** - Alternative API documentation

### DevOps & Operations
- ✅ **Docker Compose** - Complete orchestration of all services
- ✅ **Health Checks** - Service health monitoring
- ✅ **Logging** - Centralized logging for all components
- ✅ **Resource Limits** - CPU and memory constraints configured
- ✅ **Makefile** - Easy management commands
- ✅ **Init Scripts** - Automated setup and initialization

## Architecture Implementation

```
User Interface Layer:
  - Streamlit (Port 80 via Nginx)
  - Swagger UI (http://localhost/docs)

API Gateway Layer:
  - Nginx with rate limiting
  - Request routing
  - WebSocket support for Streamlit

Application Layer:
  - FastAPI (Python 3.11)
  - LangChain orchestration
  - Pydantic validation
  - Async operations

Service Layer:
  - Document Processor (pypdf, text splitters)
  - Embedding Service (sentence-transformers)
  - Vector Store (Weaviate client)
  - LLM Service (Ollama client)
  - RAG Service (orchestration)

Data Layer:
  - Weaviate (Vector embeddings)
  - MariaDB (Metadata, chat history, metrics)
  - Redis (Cache)
  - Ollama (Model storage)

Monitoring Layer:
  - Prometheus (Metrics)
  - Health check endpoints
  - Structured logging
```

## Key Features

### 1. Document Management
- Upload PDF files
- Upload text files
- Add text content directly via API
- List all documents
- Delete documents
- Automatic chunking with overlap
- Metadata support

### 2. Query Capabilities
- Semantic search across documents
- Context-aware responses
- Configurable parameters (top_k, temperature)
- Session-based chat history
- Source attribution

### 3. Performance Optimizations
- Redis caching for embeddings
- Batch processing for multiple documents
- Connection pooling
- Async operations where applicable

### 4. Production Features
- Health check endpoints for all services
- Prometheus metrics collection
- Request rate limiting
- Error handling and validation
- Database migrations
- Structured logging
- Resource constraints

### 5. Developer Experience
- Comprehensive API documentation
- One-command setup (`make init`)
- Hot-reload for development
- Clear error messages
- Type hints throughout

## File Structure

```
zee-prod-rag/
├── app/                          # FastAPI Application
│   ├── api/                      # API Endpoints
│   │   ├── __init__.py
│   │   ├── health.py            # Health checks
│   │   ├── query.py             # RAG queries
│   │   └── documents.py         # Document management
│   ├── core/                     # Core configuration
│   │   ├── __init__.py
│   │   ├── config.py            # Settings management
│   │   └── logging.py           # Logging setup
│   ├── db/                       # Database
│   │   ├── __init__.py
│   │   └── session.py           # DB session management
│   ├── models/                   # SQLAlchemy models
│   │   ├── __init__.py
│   │   └── database.py          # DB models
│   ├── schemas/                  # Pydantic schemas
│   │   ├── __init__.py
│   │   ├── requests.py          # Request schemas
│   │   └── responses.py         # Response schemas
│   ├── services/                 # Business logic
│   │   ├── __init__.py
│   │   ├── embedding_service.py # Embeddings
│   │   ├── vector_store.py      # Weaviate client
│   │   ├── document_processor.py# Document processing
│   │   ├── llm_service.py       # LLM integration
│   │   └── rag_service.py       # RAG orchestration
│   └── main.py                   # FastAPI app entry point
├── ui/
│   └── streamlit_app.py         # Streamlit UI
├── nginx/
│   └── nginx.conf               # Nginx configuration
├── prometheus/
│   └── prometheus.yml           # Prometheus config
├── scripts/
│   ├── init_services.sh         # Initialization script
│   ├── setup_ollama.sh          # Ollama model setup
│   └── test_api.sh              # API testing script
├── config/                       # Additional configs
├── docker-compose.yml            # Service orchestration
├── Dockerfile                    # FastAPI container
├── Dockerfile.streamlit          # Streamlit container
├── requirements.txt              # Python dependencies
├── Makefile                      # Management commands
├── .env.example                  # Environment template
├── .gitignore                    # Git ignore rules
├── .dockerignore                 # Docker ignore rules
├── README.md                     # Full documentation
├── QUICKSTART.md                 # Quick start guide
└── PROJECT_SUMMARY.md            # This file
```

## Technology Choices

### Why These Technologies?

1. **Ollama (llama3.2:1b)** - Smallest available model, runs locally, no API costs
2. **Weaviate** - Production-grade vector DB with excellent performance
3. **sentence-transformers** - High-quality embeddings, runs locally
4. **FastAPI** - Modern, fast, auto-documentation
5. **LangChain** - Standard orchestration framework
6. **Nginx** - Industry-standard reverse proxy
7. **MariaDB** - Reliable, MySQL-compatible
8. **Redis** - Fast caching with minimal overhead
9. **Streamlit** - Quick, Python-native UI development
10. **Prometheus** - Standard monitoring solution

## API Endpoints

### Health
- `GET /api/v1/health` - System health check

### Documents
- `POST /api/v1/documents/upload` - Upload file (PDF/TXT)
- `POST /api/v1/documents/text` - Add text document
- `GET /api/v1/documents` - List all documents
- `DELETE /api/v1/documents/{id}` - Delete document

### Query
- `POST /api/v1/query` - Query the RAG system

### Monitoring
- `GET /metrics` - Prometheus metrics

## Database Schema

### Tables

**documents**
- document_id (UUID)
- filename
- file_type
- file_size
- content_hash
- chunk_count
- metadata (JSON)
- created_at
- updated_at

**chat_history**
- id
- session_id
- user_message
- assistant_message
- context_documents (JSON)
- response_time
- created_at

**query_metrics**
- id
- query
- embedding_time
- search_time
- llm_time
- total_time
- results_count
- created_at

## Resource Requirements

### Minimum
- 8GB RAM
- 4 CPU cores
- 10GB disk space

### Recommended
- 16GB RAM
- 8 CPU cores
- 20GB disk space

### Actual Usage (Idle)
- Ollama: ~2GB RAM
- Weaviate: ~500MB RAM
- FastAPI: ~300MB RAM
- MariaDB: ~200MB RAM
- Redis: ~50MB RAM
- Nginx: ~10MB RAM
- Streamlit: ~200MB RAM
- Prometheus: ~100MB RAM

**Total: ~3.5GB RAM**

## Getting Started

### Quick Start (3 steps)
```bash
# 1. Initialize (downloads model, builds images)
make init

# 2. Access UI
open http://localhost

# 3. Upload documents and start chatting!
```

### Manual Start
```bash
# Copy environment file
cp .env.example .env

# Build images
docker-compose build

# Start services
docker-compose up -d

# Download model
docker exec rag-ollama ollama pull llama3.2:1b
```

## Testing

### Test via Script
```bash
chmod +x scripts/test_api.sh
./scripts/test_api.sh
```

### Test via UI
1. Open http://localhost
2. Upload a test document
3. Ask questions in chat

### Test via API
```bash
# Check health
curl http://localhost/api/v1/health

# Upload document
curl -X POST http://localhost/api/v1/documents/upload \
  -F "file=@test.pdf"

# Query
curl -X POST http://localhost/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "test question"}'
```

## Monitoring

- **Prometheus**: http://localhost:9090
- **API Metrics**: http://localhost/metrics
- **Health Check**: http://localhost/api/v1/health
- **Logs**: `docker-compose logs -f`

## Security Notes

This is configured for **local development**. For production:

1. Change all passwords in `.env`
2. Enable authentication on all services
3. Add SSL/TLS certificates
4. Restrict network access
5. Use secrets management
6. Enable audit logging
7. Implement proper RBAC

## Customization

### Use Different LLM Model
```bash
# Pull model
docker exec rag-ollama ollama pull mistral:7b

# Update .env
OLLAMA_MODEL=mistral:7b

# Restart
docker-compose restart fastapi
```

### Adjust Chunking Strategy
Edit `.env`:
```bash
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

### Change Resource Limits
Edit `docker-compose.yml` under each service's `deploy.resources` section.

## Maintenance

### Backup Data
```bash
make backup-db
```

### View Logs
```bash
make logs
# or
docker-compose logs -f [service-name]
```

### Clean Everything
```bash
make clean  # Removes all data!
```

### Update Services
```bash
docker-compose pull
docker-compose up -d
```

## Performance Tuning

1. **Faster queries**: Increase `REDIS_CACHE_TTL`
2. **Better accuracy**: Increase `CHUNK_SIZE` and `top_k`
3. **Faster processing**: Decrease `CHUNK_SIZE`
4. **Better responses**: Use larger model (e.g., mistral:7b)
5. **Lower memory**: Use llama3.2:1b, reduce batch sizes

## Known Limitations

1. **Model Size**: llama3.2:1b is optimized for size, not accuracy
2. **No GPU Support**: CPU-only inference (slower)
3. **Local Only**: Not configured for distributed deployment
4. **English Only**: Model and embeddings optimized for English
5. **File Types**: Only PDF and TXT supported (extensible)

## Future Enhancements

Possible additions:
- Multi-language support
- More document types (DOCX, PPTX, etc.)
- Advanced chunking strategies
- Re-ranking models
- User authentication
- Multi-tenancy
- Distributed deployment
- GPU support

## Support

1. Check `README.md` for detailed docs
2. View logs: `make logs`
3. Check health: `make health`
4. Review API docs: http://localhost/docs

## License

Provided as-is for educational and development purposes.

---

**Built with**: FastAPI, LangChain, Weaviate, Ollama, sentence-transformers, Streamlit, and Docker.
