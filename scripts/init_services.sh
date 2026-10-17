#!/bin/bash
# Initialize all services

set -e

echo "======================================"
echo "Production RAG System - Initialization"
echo "======================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

echo "Step 1: Creating .env file from template..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ .env file created. Please review and update passwords before production use."
else
    echo "✓ .env file already exists"
fi
echo ""

echo "Step 2: Building Docker images..."
docker-compose build
echo "✓ Docker images built successfully"
echo ""

echo "Step 3: Starting services..."
docker-compose up -d
echo "✓ Services started"
echo ""

echo "Step 4: Waiting for services to be healthy..."
sleep 30
echo ""

echo "Step 5: Checking service health..."
docker-compose ps
echo ""

echo "Step 6: Downloading Ollama model (llama3.2:1b - ~700MB)..."
echo "This may take a few minutes depending on your internet connection..."
sleep 10
docker exec rag-ollama ollama pull llama3.2:1b
echo "✓ Model downloaded successfully"
echo ""

echo "======================================"
echo "Initialization Complete!"
echo "======================================"
echo ""
echo "Services are now running:"
echo "  - Streamlit UI:        http://localhost"
echo "  - API Documentation:   http://localhost/docs"
echo "  - API Health Check:    http://localhost/api/v1/health"
echo "  - Prometheus:          http://localhost:9090"
echo ""
echo "To view logs:"
echo "  docker-compose logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose down"
echo ""
echo "To stop and remove all data:"
echo "  docker-compose down -v"
echo ""
