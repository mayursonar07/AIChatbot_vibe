#!/bin/bash

echo "Testing typo and variation detection for 'how' questions..."
echo ""

# Test 1: With typo "wnsure" instead of "ensure"
echo "Test 1: How do you wnsure that these are from investment domains?"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do you wnsure that these are from investment domains?",
    "session_id": "test_typo_1"
  }' | jq '.'

echo ""
echo "---"
echo ""

# Test 2: Without "how" but asking about ensuring domain
echo "Test 2: Can you ensure these entities are from investment domain?"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Can you ensure these entities are from investment domain?",
    "session_id": "test_typo_2"
  }' | jq '.'

echo ""
echo "---"
echo ""

# Test 3: Asking about validation without "how"
echo "Test 3: Verify that these are from the correct investment domain"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Verify that these are from the correct investment domain",
    "session_id": "test_typo_3"
  }' | jq '.'

echo ""
echo "---"
echo ""

# Test 4: Different variation with "confirm"
echo "Test 4: How can you confirm these belong to investment domain?"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How can you confirm these belong to investment domain?",
    "session_id": "test_typo_4"
  }' | jq '.'

echo ""
echo "---"
echo ""

# Test 5: Regular entity search (should still work normally)
echo "Test 5: Find entities related to investment banking"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Find entities related to investment banking",
    "session_id": "test_typo_5"
  }' | jq '.'

echo ""
echo "---"
echo ""

# Test 6: With typo "ensur" (missing 'e')
echo "Test 6: How do you ensur these entities from investment domain?"
curl -X POST http://localhost:8000/api/match-entity \
  -H "Content-Type: application/json" \
  -d '{
    "query": "How do you ensur these entities from investment domain?",
    "session_id": "test_typo_6"
  }' | jq '.'
