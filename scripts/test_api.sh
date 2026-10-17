#!/bin/bash
# Test script for RAG API endpoints

set -e

API_BASE="http://localhost/api/v1"
echo "Testing Production RAG System API"
echo "=================================="
echo ""

# Test 1: Health Check
echo "Test 1: Health Check"
echo "--------------------"
curl -s "${API_BASE}/health" | python3 -m json.tool
echo ""
echo ""

# Test 2: Add a text document
echo "Test 2: Adding a text document"
echo "-------------------------------"
RESPONSE=$(curl -s -X POST "${API_BASE}/documents/text" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "The quick brown fox jumps over the lazy dog. This is a test document for the RAG system. It contains information about animals and their behavior.",
    "filename": "test_document.txt",
    "metadata": {
      "tags": ["test", "animals"],
      "source": "test_script"
    }
  }')

echo "$RESPONSE" | python3 -m json.tool
DOCUMENT_ID=$(echo "$RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['document_id'])" 2>/dev/null || echo "")
echo ""
echo "Document ID: $DOCUMENT_ID"
echo ""

# Test 3: List documents
echo "Test 3: Listing documents"
echo "-------------------------"
curl -s "${API_BASE}/documents" | python3 -m json.tool
echo ""
echo ""

# Test 4: Query the system
echo "Test 4: Querying the system"
echo "---------------------------"
curl -s -X POST "${API_BASE}/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What animals are mentioned?",
    "top_k": 3,
    "temperature": 0.7
  }' | python3 -m json.tool
echo ""
echo ""

# Test 5: Delete the document
if [ -n "$DOCUMENT_ID" ]; then
  echo "Test 5: Deleting the document"
  echo "-----------------------------"
  curl -s -X DELETE "${API_BASE}/documents/${DOCUMENT_ID}" | python3 -m json.tool
  echo ""
fi

echo ""
echo "=================================="
echo "All tests completed!"
echo "=================================="
