#!/bin/bash

echo "Testing 'how' question detection in entity matching..."
echo ""

# Test 1: "How do you ensure" question
echo "Test 1: How do you ensure entities are from investment domain?"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how do you ensure that these above entities are from investment domain",
    "session_id": "test_session_1"
  }' | jq '.'

echo ""
echo "---"
echo ""

# Test 2: "How does" question
echo "Test 2: How does the matching process work?"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "how does the entity matching process work",
    "session_id": "test_session_2"
  }' | jq '.'

echo ""
echo "---"
echo ""

# Test 3: Regular entity query (should still match entities)
echo "Test 3: Regular entity query - find mutual fund entities"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "show me mutual fund entities",
    "session_id": "test_session_3"
  }' | jq '.'

echo ""
echo "---"
echo ""

# Test 4: "What is the process" question
echo "Test 4: What is the process for validating entities?"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "what is the process for validating entities",
    "session_id": "test_session_4"
  }' | jq '.'
