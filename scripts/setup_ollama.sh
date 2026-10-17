#!/bin/bash
# Script to pull Ollama model after container startup

echo "Waiting for Ollama service to be ready..."
sleep 10

echo "Pulling llama3.2:1b model (smallest model)..."
docker exec rag-ollama ollama pull llama3.2:1b

echo "Model pulled successfully!"
echo "Available models:"
docker exec rag-ollama ollama list
