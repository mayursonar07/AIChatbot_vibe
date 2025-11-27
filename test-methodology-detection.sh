#!/bin/bash

echo "=== Testing Methodology Question Detection ==="
echo ""

# Test with chat endpoint (the most common use case)
echo "1. Testing /api/chat with typo 'wnsure':"
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How do you wnsure that these entities are from investment domains?", "session_id": "test1", "use_rag": true}' \
  | jq '.response' | head -5

echo ""
echo "---"
echo ""

# Test with different phrasing
echo "2. Testing /api/chat with 'ensure these are from':"
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "ensure these entities are from investment domain", "session_id": "test2", "use_rag": true}' \
  | jq '.response' | head -5

echo ""
echo "---"
echo ""

# Test with entity matching endpoint
echo "3. Testing /api/match-entity with typo 'wnsure':"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{"query": "How do you wnsure that these are from investment domain?", "session_id": "test3"}' \
  | jq '.explanation' | head -5

echo ""
echo "---"
echo ""

# Test regular entity query (should still work)
echo "4. Testing /api/chat with regular entity query:"
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "show me custodian entities", "session_id": "test4", "use_rag": true}' \
  | jq '.response' | head -5
