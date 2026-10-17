# Production RAG System

A production-grade Retrieval-Augmented Generation (RAG) system built with FastAPI, LangChain, Weaviate, and Ollama. All services run locally in Docker containers.

## Architecture

```
┌─────────────┐
│  Streamlit  │  ← User Interface (Port 80)
│     UI      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────┐
│   Nginx (API Gateway/Load Balancer) │  ← Port 80
└──────────┬──────────────────────────┘
           │
           ▼
┌──────────────────────────────────────┐
│  FastAPI Application (Port 8000)     │
│  ┌────────────────────────────────┐  │
│  │  LangChain Orchestration       │  │
│  │  - Prompt Templates            │  │
│  │  - Chain Management            │  │
│  │  - Memory Management           │  │
│  └────────────────────────────────┘  │
└──────┬───────────────────┬───────────┘
       │                   │
       ▼                   ▼
┌─────────────┐    ┌──────────────────┐
│   Ollama    │    │  Weaviate Vector │
│   LLM API   │    │     Database     │
│  (Port      │    │   (Port 8080)    │
│   11434)    │    │                  │
└─────────────┘    └──────────────────┘
       │                   │
       └─────────┬─────────┘
                 ▼
       ┌──────────────────┐
       │ Sentence-Trans-  │
       │   formers        │
       │ Embedding Model  │
       │ (all-MiniLM-L6-v2)│
       └──────────────────┘

    Additional Services:
    - Redis (Cache - Port 6379)
    - MariaDB (Metadata - Port 3306)
    - Prometheus (Monitoring - Port 9090)
```

## Features

- **Document Processing**: Upload and process PDF and text documents
- **Semantic Search**: Vector similarity search using Weaviate
- **LLM Integration**: Local LLM inference with Ollama (llama3.2:1b)
- **Embedding Cache**: Redis caching for embeddings and responses
- **Chat History**: Persistent conversation history in MariaDB
- **Production Ready**:
  - Nginx API gateway with rate limiting
  - Health checks for all services
  - Prometheus monitoring
  - Docker orchestration
  - Resource limits configured
- **Interactive UI**: Streamlit web interface
- **REST API**: Comprehensive FastAPI endpoints with Swagger documentation

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Framework | FastAPI | REST API and orchestration |
| LLM | Ollama (llama3.2:1b) | Language model inference |
| Orchestration | LangChain | RAG pipeline management |
| Vector DB | Weaviate | Document embeddings storage |
| Embeddings | sentence-transformers | Text-to-vector conversion |
| Cache | Redis | Embedding and response caching |
| Database | MariaDB | Metadata and chat history |
| API Gateway | Nginx | Load balancing and rate limiting |
| Monitoring | Prometheus | Metrics collection |
| UI | Streamlit | Web interface |

## Prerequisites

- Docker and Docker Compose
- At least 8GB RAM available for Docker
- 10GB free disk space (for models and data)

## Quick Start

### 1. Clone and Initialize

```bash
# Clone or navigate to the project directory
cd zee-prod-rag

# Initialize all services (first time setup)
make init
```

This will:
- Create `.env` file
- Build Docker images
- Start all services
- Download the Ollama model (~700MB)

### 2. Access the System

Once initialization is complete:

- **Web UI**: http://localhost
- **API Documentation**: http://localhost/docs
- **API Health**: http://localhost/api/v1/health
- **Prometheus**: http://localhost:9090

## Usage

### Using the Streamlit UI

1. Open http://localhost in your browser
2. Go to the **Documents** tab to upload PDF or text files
3. Switch to the **Chat** tab to ask questions
4. View your document library in the **Document Library** tab

### Using the REST API

#### Upload a Document

```bash
curl -X POST "http://localhost/api/v1/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/document.pdf"
```

#### Add Text Document

```bash
curl -X POST "http://localhost/api/v1/documents/text" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Your document content here",
    "filename": "my_document.txt"
  }'
```

#### Query the System

```bash
curl -X POST "http://localhost/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What is this document about?",
    "top_k": 5,
    "temperature": 0.7
  }'
```

#### List Documents

```bash
curl http://localhost/api/v1/documents
```

#### Delete Document

```bash
curl -X DELETE "http://localhost/api/v1/documents/{document_id}"
```

## Management Commands

### Using Make

```bash
make help           # Show all available commands
make up             # Start all services
make down           # Stop all services
make logs           # View logs from all services
make health         # Check service health
make restart        # Restart all services
make clean          # Remove all data (WARNING: destructive)
```

### Using Docker Compose Directly

```bash
# Start services
docker compose up -d

# Stop services
docker compose down

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f fastapi
docker compose logs -f ollama

# Check service status
docker compose ps

# Restart specific service
docker compose restart fastapi
```

## Configuration

### Environment Variables

Edit `.env` file to customize:

```bash
# LLM Configuration
OLLAMA_MODEL=llama3.2:1b        # Model to use
OLLAMA_TEMPERATURE=0.7           # Response creativity
OLLAMA_MAX_TOKENS=2048           # Max response length

# Document Processing
CHUNK_SIZE=1000                  # Text chunk size
CHUNK_OVERLAP=200                # Chunk overlap

# Cache
REDIS_CACHE_TTL=3600            # Cache TTL in seconds

# Embedding
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
```

### Resource Limits

Default resource allocations in `docker-compose.yml`:

- **Ollama**: 8GB RAM, 4 CPUs (for LLM inference)
- **FastAPI**: 4GB RAM, 2 CPUs
- **Weaviate**: 4GB RAM, 2 CPUs
- **MariaDB**: 2GB RAM, 2 CPUs
- **Redis**: 1GB RAM, 1 CPU

Adjust based on your system:

```yaml
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 4G
```

## Monitoring

### Health Checks

```bash
# Check all services
make health

# Or visit
curl http://localhost/api/v1/health
```

### Prometheus Metrics

Access Prometheus at http://localhost:9090

Available metrics:
- Request rates and latencies
- Error rates
- Service health
- Resource usage

### View Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f fastapi
docker compose logs -f ollama
docker compose logs -f weaviate
```

## Models

### Default Model

- **llama3.2:1b** (~700MB) - Smallest model, good for testing and low-resource environments

### Using Different Models

To use a different Ollama model:

1. Pull the model:
```bash
docker exec rag-ollama ollama pull llama3.2:3b
# or
docker exec rag-ollama ollama pull mistral:7b
```

2. Update `.env`:
```bash
OLLAMA_MODEL=llama3.2:3b
```

3. Restart FastAPI:
```bash
docker compose restart fastapi
```

Available models:
- `llama3.2:1b` - 700MB (fastest, least accurate)
- `llama3.2:3b` - 2GB (balanced)
- `phi3:mini` - 2.3GB (Microsoft)
- `mistral:7b` - 4GB (high quality)

List available models:
```bash
docker exec rag-ollama ollama list
```

## Troubleshooting

### Services Not Starting

```bash
# Check service status
docker compose ps

# View logs for failing service
docker compose logs [service-name]

# Restart specific service
docker compose restart [service-name]
```

### Ollama Model Not Found

```bash
# Pull the model manually
docker exec rag-ollama ollama pull llama3.2:1b

# Verify model is available
docker exec rag-ollama ollama list
```

### Database Connection Issues

```bash
# Check MariaDB logs
docker compose logs mariadb

# Verify database is healthy
docker compose ps mariadb

# Restart database
docker compose restart mariadb
```

### High Memory Usage

1. Reduce model size (use llama3.2:1b instead of larger models)
2. Adjust resource limits in `docker-compose.yml`
3. Reduce `CHUNK_SIZE` and `EMBEDDING_BATCH_SIZE` in `.env`

### Port Conflicts

If port 80 is already in use:

```yaml
# Edit docker-compose.yml
nginx:
  ports:
    - "8080:80"  # Change to different port
```

Access UI at http://localhost:8080

## Database Management

### Backup Database

```bash
make backup-db
```

Backups are saved to `backups/` directory.

### Access Database

```bash
# Using Make
make shell-db

# Or directly
docker exec -it rag-mariadb mysql -urag_user -prag_password_change_in_production rag_metadata
```

### View Chat History

```sql
SELECT * FROM chat_history ORDER BY created_at DESC LIMIT 10;
```

### View Metrics

```sql
SELECT * FROM query_metrics ORDER BY created_at DESC LIMIT 10;
```

## Data Persistence

All data is stored in Docker volumes:

- `ollama-data`: Model files
- `weaviate-data`: Vector embeddings
- `mariadb-data`: Metadata and chat history
- `redis-data`: Cache
- `prometheus-data`: Metrics

### Backup Volumes

```bash
# Backup all volumes
docker run --rm -v ollama-data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz -C /data .
```

### Remove All Data

```bash
make clean  # This will prompt for confirmation
```

## Development

### Project Structure

```
zee-prod-rag/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Configuration and logging
│   ├── db/               # Database setup
│   ├── models/           # Database models
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   └── main.py           # FastAPI app
├── ui/
│   └── streamlit_app.py  # Streamlit UI
├── nginx/
│   └── nginx.conf        # Nginx configuration
├── prometheus/
│   └── prometheus.yml    # Prometheus config
├── scripts/              # Setup scripts
├── docker-compose.yml    # Service orchestration
├── Dockerfile            # FastAPI image
├── Dockerfile.streamlit  # Streamlit image
├── requirements.txt      # Python dependencies
├── Makefile              # Management commands
└── README.md            # This file
```

### Modifying Code

The application code is mounted as volumes, so changes are reflected immediately (for development):

```yaml
volumes:
  - ./app:/app/app  # FastAPI code
  - ./ui:/app       # Streamlit code
```

For production, remove volumes and rebuild images.

## Security Considerations

**Important**: This is a local development setup. For production deployment:

1. Change all default passwords in `.env`
2. Enable authentication in Weaviate
3. Add SSL/TLS certificates to Nginx
4. Restrict network access
5. Enable authentication on all services
6. Use secrets management (Docker secrets, Vault, etc.)
7. Implement proper access controls
8. Enable audit logging

## API Documentation

Full API documentation is available at:
- **Swagger UI**: http://localhost/docs
- **ReDoc**: http://localhost/redoc

## Performance Tips

1. **Adjust chunk size**: Smaller chunks = more accurate but slower
2. **Tune top_k**: More results = better context but slower
3. **Use caching**: Redis caching significantly improves repeat queries
4. **Model selection**: Smaller models are faster but less accurate
5. **Resource allocation**: Increase RAM/CPU for Ollama and Weaviate for better performance

## License

This project is provided as-is for educational and development purposes.

## Support

For issues and questions:
1. Check logs: `make logs`
2. Verify health: `make health`
3. Review this README
4. Check individual service documentation

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://www.langchain.com/)
- [Ollama](https://ollama.ai/)
- [Weaviate](https://weaviate.io/)
- [Sentence Transformers](https://www.sbert.net/)
- [Streamlit](https://streamlit.io/)
