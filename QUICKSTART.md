# Quick Start Guide

Get your RAG system running in 3 steps!

## Step 1: Start the System

```bash
make init
```

This will take 5-10 minutes to:
- Build Docker images
- Download the LLM model (~700MB)
- Initialize all services

## Step 2: Access the UI

Open your browser to: **http://localhost**

## Step 3: Upload a Document & Chat

1. Go to **Documents** tab
2. Upload a PDF or text file
3. Go to **Chat** tab
4. Ask questions about your document!

---

## Example Usage

### Upload via UI
1. Click "Documents" tab
2. Choose "File Upload"
3. Select a PDF or TXT file
4. Click "Upload Document"

### Query via UI
1. Click "Chat" tab
2. Type: "What is this document about?"
3. Get AI-powered answers!

### Query via API

```bash
# Upload a document
curl -X POST "http://localhost/api/v1/documents/upload" \
  -F "file=@document.pdf"

# Ask a question
curl -X POST "http://localhost/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the main topic?"}'
```

---

## Useful Links

- **UI**: http://localhost
- **API Docs**: http://localhost/docs
- **Health Check**: http://localhost/api/v1/health
- **Monitoring**: http://localhost:9090

---

## Common Commands

```bash
make up        # Start services
make down      # Stop services
make logs      # View logs
make health    # Check status
make restart   # Restart all
```

---

## Troubleshooting

**Services not starting?**
```bash
docker-compose ps              # Check status
docker-compose logs [service]  # View logs
```

**Model not found?**
```bash
docker exec rag-ollama ollama pull llama3.2:1b
```

**Need more help?** See [README.md](README.md)
