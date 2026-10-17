#!/bin/bash
# Verification script for Production RAG System

set -e

echo "=========================================="
echo "Production RAG System - Setup Verification"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check Docker
echo "1. Checking Docker..."
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker is running"
else
    echo -e "${RED}✗${NC} Docker is not running"
    exit 1
fi
echo ""

# Check Docker Compose
echo "2. Checking Docker Compose..."
if docker compose version > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Docker Compose is available"
else
    echo -e "${RED}✗${NC} Docker Compose is not available"
    exit 1
fi
echo ""

# Check .env file
echo "3. Checking .env file..."
if [ -f .env ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
else
    echo -e "${YELLOW}!${NC} .env file not found, creating from template..."
    cp .env.example .env
    echo -e "${GREEN}✓${NC} .env file created"
fi
echo ""

# Check services status
echo "4. Checking services status..."
if docker compose ps | grep -q "Up"; then
    docker compose ps
    echo -e "${GREEN}✓${NC} Services are running"
else
    echo -e "${YELLOW}!${NC} Services are not running"
    echo "Run 'make init' or 'docker compose up -d' to start services"
fi
echo ""

# Check individual service health
echo "5. Checking individual services..."

# Check Nginx
echo -n "   Nginx (API Gateway): "
if curl -s http://localhost > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Check FastAPI
echo -n "   FastAPI (Application): "
if curl -s http://localhost/api/v1/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Check Weaviate
echo -n "   Weaviate (Vector DB): "
if curl -s http://localhost:8080/v1/.well-known/ready > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Check Ollama
echo -n "   Ollama (LLM): "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Check MariaDB
echo -n "   MariaDB (Database): "
if docker exec rag-mariadb mysqladmin ping -h localhost --silent > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Check Redis
echo -n "   Redis (Cache): "
if docker exec rag-redis redis-cli ping | grep -q PONG; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

# Check Prometheus
echo -n "   Prometheus (Monitoring): "
if curl -s http://localhost:9090/-/healthy > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
fi

echo ""

# Check Ollama model
echo "6. Checking Ollama model..."
if docker exec rag-ollama ollama list 2>/dev/null | grep -q "llama3.2:1b"; then
    echo -e "${GREEN}✓${NC} llama3.2:1b model is available"
else
    echo -e "${YELLOW}!${NC} llama3.2:1b model not found"
    echo "Run './scripts/setup_ollama.sh' to download the model"
fi
echo ""

# Check API documentation
echo "7. Checking API documentation..."
if curl -s http://localhost/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} API documentation is accessible at http://localhost/docs"
else
    echo -e "${RED}✗${NC} API documentation is not accessible"
fi
echo ""

# Check disk space
echo "8. Checking disk space..."
AVAILABLE=$(df -h . | awk 'NR==2 {print $4}')
echo "   Available space: $AVAILABLE"
echo ""

# Summary
echo "=========================================="
echo "Verification Summary"
echo "=========================================="
echo ""
echo "If all checks passed (${GREEN}✓${NC}), your system is ready!"
echo ""
echo "Access points:"
echo "  - Web UI:          http://localhost"
echo "  - API Docs:        http://localhost/docs"
echo "  - Health Check:    http://localhost/api/v1/health"
echo "  - Prometheus:      http://localhost:9090"
echo ""
echo "Next steps:"
echo "  1. Open http://localhost in your browser"
echo "  2. Upload a document in the 'Documents' tab"
echo "  3. Ask questions in the 'Chat' tab"
echo ""
echo "For help: cat README.md or cat QUICKSTART.md"
echo ""
