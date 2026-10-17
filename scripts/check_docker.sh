#!/bin/bash
# Check Docker and Docker Compose compatibility

echo "Checking Docker setup..."
echo ""

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running or not installed"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✓ Docker is running"
docker --version
echo ""

# Check Docker Compose (V2 - new version)
if docker compose version > /dev/null 2>&1; then
    echo "✓ Docker Compose V2 is available"
    docker compose version
    echo ""
    echo "👍 You're all set! Use: make init"
    exit 0
fi

# Check Docker Compose (V1 - old version)
if docker-compose version > /dev/null 2>&1; then
    echo "⚠️  Docker Compose V1 (legacy) detected"
    docker-compose version
    echo ""
    echo "Please upgrade to Docker Compose V2:"
    echo "  - Update Docker Desktop to latest version"
    echo "  - Or install: https://docs.docker.com/compose/install/"
    echo ""
    echo "Alternatively, you can use 'docker-compose' commands directly:"
    echo "  docker-compose build"
    echo "  docker-compose up -d"
    exit 1
fi

# No Docker Compose found
echo "❌ Docker Compose not found"
echo ""
echo "Please install Docker Desktop (includes Docker Compose):"
echo "  https://www.docker.com/products/docker-desktop"
exit 1
