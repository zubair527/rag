# System Architecture Documentation

## Overview

This document provides detailed architecture information for the RAG system.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Layer                           │
│                                                              │
│  ┌──────────────┐              ┌──────────────┐            │
│  │  Web Browser │              │  API Client  │            │
│  │  (Streamlit) │              │   (curl/SDK) │            │
│  └──────┬───────┘              └──────┬───────┘            │
└─────────┼──────────────────────────────┼──────────────────┘
          │                              │
          └──────────────┬───────────────┘
                         │
          ┌──────────────▼──────────────┐
          │   Nginx (Port 80)           │
          │   - Load Balancing          │
          │   - Rate Limiting           │
          │   - SSL Termination (ready) │
          └──────────────┬──────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
┌─────────▼─────────┐       ┌───────────▼────────┐
│  Streamlit UI     │       │  FastAPI App       │
│  (Port 8501)      │       │  (Port 8000)       │
│                   │       │                    │
│  - Document UI    │       │  - REST API        │
│  - Chat Interface │       │  - Business Logic  │
│  - Monitoring     │       │  - Orchestration   │
└───────────────────┘       └─────────┬──────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
          ┌─────────▼─────┐  ┌────────▼────────┐  ┌────▼─────┐
          │  Ollama LLM   │  │   Weaviate      │  │  Redis   │
          │  (Port 11434) │  │  Vector DB      │  │  Cache   │
          │               │  │  (Port 8080)    │  │ (Port    │
          │  - llama3.2   │  │                 │  │  6379)   │
          │  - Inference  │  │  - Embeddings   │  │          │
          └───────────────┘  │  - Search       │  └──────────┘
                             └─────────────────┘
                                      │
                             ┌────────▼────────┐
                             │   MariaDB       │
                             │  (Port 3306)    │
                             │                 │
                             │  - Metadata     │
                             │  - Chat History │
                             │  - Metrics      │
                             └─────────────────┘
```

## Component Architecture

### 1. API Gateway (Nginx)

**Purpose**: Entry point for all requests

**Responsibilities**:
- Load balancing between services
- Rate limiting (10 req/s for API, 2 req/s for uploads)
- Request routing
- WebSocket proxying for Streamlit
- Static file serving (future)

**Configuration**: [nginx/nginx.conf](nginx/nginx.conf)

### 2. Application Layer (FastAPI)

**Purpose**: Core business logic and orchestration

**Components**:

```
app/
├── api/                    # HTTP Endpoints
│   ├── health.py          # Health checks
│   ├── query.py           # RAG queries
│   └── documents.py       # Document CRUD
├── core/                   # Core utilities
│   ├── config.py          # Configuration
│   └── logging.py         # Logging setup
├── services/               # Business logic
│   ├── rag_service.py     # RAG orchestration
│   ├── llm_service.py     # LLM integration
│   ├── embedding_service.py # Embeddings
│   ├── vector_store.py    # Vector DB client
│   └── document_processor.py # Doc processing
├── models/                 # Database models
├── schemas/                # Request/Response schemas
└── db/                     # Database session
```

**Key Patterns**:
- Dependency injection for services
- Service layer pattern
- Repository pattern for data access
- Async operations where beneficial

### 3. LLM Service (Ollama)

**Purpose**: Language model inference

**Model**: llama3.2:1b (~700MB)

**Capabilities**:
- Question answering
- Context-based generation
- Temperature control
- Token limit management

**API**: HTTP REST API on port 11434

### 4. Vector Database (Weaviate)

**Purpose**: Store and search document embeddings

**Schema**:
```
Collection: Documents
├── document_id: TEXT
├── content: TEXT
├── chunk_index: INT
├── filename: TEXT
├── file_type: TEXT
├── metadata: TEXT
└── vector: [384 dimensions]
```

**Features**:
- HNSW index for fast similarity search
- Cosine distance metric
- Batch operations
- Filtering support

### 5. Embedding Service

**Model**: sentence-transformers/all-MiniLM-L6-v2

**Specifications**:
- Embedding dimension: 384
- Max sequence length: 256 tokens
- Model size: ~80MB

**Caching Strategy**:
- SHA-256 hash of input text as key
- TTL: 1 hour (configurable)
- Storage: Redis

### 6. Cache Layer (Redis)

**Purpose**: High-speed caching

**Cached Data**:
1. Text embeddings
2. Search results (future)
3. LLM responses (future)

**Configuration**:
- Max memory: 512MB
- Eviction: allkeys-lru
- Persistence: AOF enabled

### 7. Database (MariaDB)

**Purpose**: Persistent metadata storage

**Tables**:

**documents**:
```sql
CREATE TABLE documents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    document_id VARCHAR(255) UNIQUE,
    filename VARCHAR(512),
    file_type VARCHAR(50),
    file_size INT,
    content_hash VARCHAR(64),
    chunk_count INT,
    metadata JSON,
    created_at DATETIME,
    updated_at DATETIME
);
```

**chat_history**:
```sql
CREATE TABLE chat_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    session_id VARCHAR(255),
    user_message TEXT,
    assistant_message TEXT,
    context_documents JSON,
    response_time FLOAT,
    created_at DATETIME
);
```

**query_metrics**:
```sql
CREATE TABLE query_metrics (
    id INT PRIMARY KEY AUTO_INCREMENT,
    query TEXT,
    embedding_time FLOAT,
    search_time FLOAT,
    llm_time FLOAT,
    total_time FLOAT,
    results_count INT,
    created_at DATETIME
);
```

### 8. Monitoring (Prometheus)

**Purpose**: Metrics collection and monitoring

**Metrics Collected**:
- HTTP request counts
- Response times
- Error rates
- Service health
- Custom business metrics

**Endpoints**:
- Prometheus UI: http://localhost:9090
- Metrics endpoint: http://localhost/metrics

## Data Flow

### Document Ingestion Flow

```
1. User uploads document
   │
   ▼
2. Nginx receives request
   │
   ▼
3. FastAPI validates file
   │
   ▼
4. Document Processor extracts text
   │
   ▼
5. Text Splitter chunks document
   │
   ▼
6. Embedding Service generates vectors
   │  (checks Redis cache first)
   ▼
7. Weaviate stores embeddings
   │
   ▼
8. MariaDB stores metadata
   │
   ▼
9. Response returned to user
```

### Query Processing Flow

```
1. User submits query
   │
   ▼
2. Nginx routes to FastAPI
   │
   ▼
3. RAG Service orchestrates:
   │
   ├─▶ 4. Embedding Service
   │   │  (generates query embedding)
   │   │  (checks cache)
   │   │
   ├─▶ 5. Weaviate
   │   │  (vector similarity search)
   │   │  (returns top-k chunks)
   │   │
   ├─▶ 6. LLM Service
   │   │  (formats context)
   │   │  (generates answer)
   │   │
   └─▶ 7. MariaDB
       │  (saves chat history)
       │  (saves metrics)
       │
       ▼
8. Response with answer and sources
```

## Security Architecture

### Current Setup (Development)

```
┌─────────────────────────────────────┐
│  Public Access (Port 80)            │
│  - No authentication                │
│  - Rate limiting only               │
└─────────────────────────────────────┘
         │
┌────────▼────────────────────────────┐
│  Internal Network (Docker)          │
│  - Service-to-service no auth       │
│  - Isolated from host               │
└─────────────────────────────────────┘
```

### Production Recommendations

```
┌─────────────────────────────────────┐
│  SSL/TLS Termination (443)          │
│  - HTTPS only                       │
│  - Certificate management           │
└────────┬────────────────────────────┘
         │
┌────────▼────────────────────────────┐
│  Authentication Layer               │
│  - JWT tokens                       │
│  - API keys                         │
│  - OAuth2 (optional)                │
└────────┬────────────────────────────┘
         │
┌────────▼────────────────────────────┐
│  Authorization Layer                │
│  - RBAC                             │
│  - Resource-level permissions       │
└────────┬────────────────────────────┘
         │
┌────────▼────────────────────────────┐
│  Application Layer                  │
│  - Input validation                 │
│  - SQL injection prevention         │
│  - XSS protection                   │
└─────────────────────────────────────┘
```

## Scalability Considerations

### Current Limitations

1. **Single instance** - No horizontal scaling
2. **No queue system** - Synchronous processing
3. **Local storage** - No distributed storage
4. **CPU-only** - No GPU acceleration

### Scaling Path

**Step 1: Vertical Scaling**
- Increase container resources
- Add more CPU/RAM
- Use GPU for Ollama

**Step 2: Add Queue System**
```
User → API → Queue (RabbitMQ/Celery) → Workers → Services
```

**Step 3: Horizontal Scaling**
```
Load Balancer
    │
    ├─▶ FastAPI Instance 1
    ├─▶ FastAPI Instance 2
    └─▶ FastAPI Instance 3
         │
         └─▶ Shared Services (Redis, Weaviate, MariaDB)
```

**Step 4: Distributed Setup**
- Kubernetes deployment
- Distributed Weaviate cluster
- MariaDB replication
- Redis cluster
- Object storage for documents

## Performance Characteristics

### Latency Breakdown (Typical)

```
Total Query Time: ~2-5 seconds
├─ Embedding Generation: 50-100ms
├─ Vector Search: 50-200ms
└─ LLM Generation: 1.5-4s (depends on response length)
```

### Optimization Strategies

1. **Caching**:
   - Embedding cache hit: ~1ms
   - 70-80% cache hit rate expected

2. **Batch Processing**:
   - Process multiple embeddings together
   - Reduces overhead by 40-60%

3. **Connection Pooling**:
   - Database: 10 connections
   - Reduces connection overhead

4. **Async Operations**:
   - Non-blocking I/O where applicable
   - Better resource utilization

## Deployment Architecture

### Container Architecture

```
Docker Host
│
├─ Network: rag-network (bridge)
│
├─ Volumes:
│  ├─ ollama-data (model storage)
│  ├─ weaviate-data (vector DB)
│  ├─ mariadb-data (database)
│  ├─ redis-data (cache)
│  └─ prometheus-data (metrics)
│
└─ Containers:
   ├─ nginx (alpine) - 10MB RAM
   ├─ fastapi (python:3.11) - 300MB RAM
   ├─ streamlit (python:3.11) - 200MB RAM
   ├─ ollama (custom) - 2GB+ RAM
   ├─ weaviate (1.27.1) - 500MB+ RAM
   ├─ mariadb (11.2) - 200MB RAM
   ├─ redis (7-alpine) - 50MB RAM
   └─ prometheus (latest) - 100MB RAM
```

### Health Check Strategy

All services implement health checks:
- **Interval**: 30s
- **Timeout**: 10s
- **Retries**: 3-5
- **Start period**: 30-60s

## Monitoring Architecture

### Metrics Collection

```
Application
    │
    ├─▶ Prometheus Client Library
    │   (exports /metrics endpoint)
    │
    └─▶ Prometheus Server
        │  (scrapes every 10-30s)
        │
        └─▶ Prometheus TSDB
            (stores time-series data)
```

### Available Metrics

1. **HTTP Metrics**:
   - Request count
   - Response time (histogram)
   - Status codes

2. **Business Metrics**:
   - Documents indexed
   - Queries processed
   - Cache hit rate

3. **System Metrics**:
   - CPU usage
   - Memory usage
   - Disk I/O

## Disaster Recovery

### Backup Strategy

**What to Backup**:
1. MariaDB database (metadata, history)
2. Weaviate data (embeddings)
3. Ollama models (large, but downloadable)

**Backup Commands**:
```bash
# Database
make backup-db

# Volumes
docker run --rm \
  -v ollama-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar czf /backup/ollama.tar.gz -C /data .
```

### Recovery Strategy

1. **Restore Database**:
```bash
docker exec -i rag-mariadb mysql -u... -p... rag_metadata < backup.sql
```

2. **Restore Volumes**:
```bash
docker run --rm \
  -v ollama-data:/data \
  -v $(pwd)/backups:/backup \
  alpine tar xzf /backup/ollama.tar.gz -C /data
```

3. **Rebuild Embeddings** (if Weaviate data lost):
   - Re-upload documents via API
   - System will regenerate embeddings

## Technology Decisions

### Why These Choices?

| Technology | Alternative | Why Chosen |
|------------|-------------|------------|
| Ollama | OpenAI API | Local, no cost, privacy |
| Weaviate | Pinecone | Local, open-source |
| sentence-transformers | OpenAI Embeddings | Local, no cost |
| FastAPI | Flask | Modern, async, auto-docs |
| MariaDB | PostgreSQL | Lighter, MySQL compatible |
| Redis | Memcached | More features, persistence |
| Nginx | Traefik | Simpler, more familiar |
| Streamlit | React | Faster development, Python |

## Future Architecture Enhancements

1. **Add Message Queue**:
   - RabbitMQ or Kafka
   - Async document processing
   - Better scalability

2. **Add API Gateway**:
   - Kong or Tyk
   - Advanced rate limiting
   - API versioning
   - Analytics

3. **Add CDN**:
   - CloudFlare or similar
   - Static asset caching
   - DDoS protection

4. **Implement CQRS**:
   - Separate read/write models
   - Better performance
   - Easier scaling

5. **Add Event Sourcing**:
   - Audit trail
   - Replay capability
   - Better debugging

---

For implementation details, see [README.md](README.md)
