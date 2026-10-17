.PHONY: help build up down logs clean init setup-ollama health test

# Default target
help:
	@echo "Production RAG System - Available Commands:"
	@echo ""
	@echo "  make init          - Initialize and start all services (first time setup)"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make logs          - View logs from all services"
	@echo "  make health        - Check health of all services"
	@echo "  make setup-ollama  - Download Ollama model"
	@echo "  make clean         - Stop services and remove volumes (WARNING: deletes all data)"
	@echo "  make restart       - Restart all services"
	@echo "  make shell-api     - Open shell in FastAPI container"
	@echo "  make shell-db      - Open MySQL shell"
	@echo ""

# Initialize everything (first time setup)
init:
	@echo "Initializing Production RAG System..."
	@chmod +x scripts/check_docker.sh scripts/init_services.sh
	@./scripts/check_docker.sh
	@./scripts/init_services.sh

# Build images
build:
	docker compose build

# Start services
up:
	docker compose up -d
	@echo "Services started. Access the UI at http://localhost"

# Stop services
down:
	docker compose down

# View logs
logs:
	docker compose logs -f

# Check health
health:
	@echo "Checking service health..."
	@curl -s http://localhost/api/v1/health | python -m json.tool || echo "API not responding"

# Setup Ollama model
setup-ollama:
	@chmod +x scripts/setup_ollama.sh
	@./scripts/setup_ollama.sh

# Clean everything (removes volumes - WARNING: deletes all data)
clean:
	@echo "WARNING: This will remove all data including documents, chat history, and embeddings!"
	@read -p "Are you sure? (yes/no): " confirm && [ "$$confirm" = "yes" ] && docker compose down -v || echo "Cancelled"

# Restart services
restart: down up

# Open shell in FastAPI container
shell-api:
	docker exec -it rag-fastapi /bin/bash

# Open MySQL shell
shell-db:
	docker exec -it rag-mariadb mysql -urag_user -prag_password_change_in_production rag_metadata

# View specific service logs
logs-api:
	docker compose logs -f fastapi

logs-ui:
	docker compose logs -f streamlit

logs-ollama:
	docker compose logs -f ollama

logs-weaviate:
	docker compose logs -f weaviate

# Backup database
backup-db:
	@mkdir -p backups
	docker exec rag-mariadb mysqldump -urag_user -prag_password_change_in_production rag_metadata > backups/backup_$$(date +%Y%m%d_%H%M%S).sql
	@echo "Database backed up to backups/"

# Show running containers
ps:
	docker compose ps
