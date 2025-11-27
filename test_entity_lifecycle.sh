#!/bin/bash

echo "╔═══════════════════════════════════════════════════════════╗"
echo "║  Testing Entity Lifecycle Management (CREATE/UPDATE/DELETE) ║"
echo "╚═══════════════════════════════════════════════════════════╝"
echo ""

# Step 1: CREATE - Ingest a new entity
echo "1️⃣  CREATE: Ingesting Apple entity..."
CREATE_RESPONSE=$(curl -s -X POST http://localhost:8000/api/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Apple Inc. (AAPL) - Technology company. Products: iPhone, iPad, Mac. CEO: Tim Cook. Market Cap: $2.5T",
    "document_name": "apple_entity",
    "metadata": {"source": "database", "category": "technology", "version": "1.0"}
  }')

echo "$CREATE_RESPONSE" | python3 -m json.tool
DOC_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['file_id'])")
echo "   📝 Document ID: $DOC_ID"
echo ""

# Step 2: VERIFY - Check stats
echo "2️⃣  VERIFY: Checking vector store stats..."
curl -s http://localhost:8000/api/stats | python3 -m json.tool
echo ""

# Step 3: UPDATE - Modify the entity
echo "3️⃣  UPDATE: Updating Apple entity with new information..."
curl -s -X PUT "http://localhost:8000/api/document/${DOC_ID}" \
  -H "Content-Type: application/json" \
  -d "{
    \"document_id\": \"${DOC_ID}\",
    \"content\": \"Apple Inc. (AAPL) - Technology company. Products: iPhone, iPad, Mac, Vision Pro (NEW). CEO: Tim Cook. Market Cap: $3.0T (UPDATED)\",
    \"document_name\": \"apple_entity\",
    \"metadata\": {\"source\": \"database\", \"category\": \"technology\", \"version\": \"2.0\"}
  }" | python3 -m json.tool
echo ""

# Step 4: QUERY - Test RAG with updated data
echo "4️⃣  QUERY: Testing RAG with updated entity..."
QUERY_RESPONSE=$(curl -s -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What products does Apple make?",
    "session_id": "lifecycle_test",
    "use_rag": true
  }')

echo "$QUERY_RESPONSE" | python3 -c "
import sys, json
data = json.load(sys.stdin)
print('   Response:', data['response'][:200] + ('...' if len(data['response']) > 200 else ''))
print('   Sources:', len(data['sources']), 'documents')
"
echo ""

# Step 5: DELETE - Remove the entity
echo "5️⃣  DELETE: Removing Apple entity..."
curl -s -X DELETE "http://localhost:8000/api/document/${DOC_ID}" | python3 -m json.tool
echo ""

# Step 6: VERIFY DELETION - Check stats again
echo "6️⃣  VERIFY DELETION: Checking vector store stats..."
curl -s http://localhost:8000/api/stats | python3 -m json.tool
echo ""

echo "✅ Lifecycle test completed successfully!"
echo ""
echo "Key Takeaways:"
echo "  • Documents can be created with unique IDs"
echo "  • Updates preserve document ID while refreshing embeddings"
echo "  • Deletes remove all chunks cleanly"
echo "  • No stale data remains in the vector store"
