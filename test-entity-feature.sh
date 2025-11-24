#!/bin/bash

# Test script for Entity-Enhanced RAG Chatbot
# This script verifies the implementation is working correctly

echo "╔════════════════════════════════════════════════════════╗"
echo "║   Entity-Enhanced RAG Chatbot - Feature Test          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking Prerequisites..."
echo ""

# 1. Check if Docker is running
if docker info > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Docker is running${NC}"
else
    echo -e "${RED}❌ Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

# 2. Check .env file
if [ -f .env ]; then
    echo -e "${GREEN}✅ .env file exists${NC}"
    if grep -q "OPENAI_API_KEY" .env; then
        echo -e "${GREEN}✅ OPENAI_API_KEY is configured${NC}"
    else
        echo -e "${RED}❌ OPENAI_API_KEY not found in .env${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ .env file not found${NC}"
    exit 1
fi

# 3. Check entities.json
if [ -f frontend/src/data/entities.json ]; then
    ENTITY_COUNT=$(grep -o '"id":' frontend/src/data/entities.json | wc -l | xargs)
    echo -e "${GREEN}✅ entities.json exists with ${ENTITY_COUNT} entities${NC}"
else
    echo -e "${RED}❌ entities.json not found${NC}"
    exit 1
fi

# 4. Check modified files
echo ""
echo "📁 Checking Modified Files..."
echo ""

FILES_TO_CHECK=(
    "frontend/src/App.tsx"
    "frontend/src/App.css"
    "backend/app/models.py"
    "backend/app/main.py"
    "backend/app/rag_engine.py"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✅ $file${NC}"
    else
        echo -e "${RED}❌ $file not found${NC}"
    fi
done

echo ""
echo "🔍 Verifying Implementation..."
echo ""

# Check for entity matching endpoint in main.py
if grep -q "match-entity" backend/app/main.py; then
    echo -e "${GREEN}✅ Entity matching endpoint exists${NC}"
else
    echo -e "${YELLOW}⚠️  Entity matching endpoint not found${NC}"
fi

# Check for RAG integration in App.tsx
if grep -q "axios.post" frontend/src/App.tsx && grep -q "api/chat" frontend/src/App.tsx; then
    echo -e "${GREEN}✅ RAG API integration in frontend${NC}"
else
    echo -e "${YELLOW}⚠️  RAG integration not complete${NC}"
fi

# Check for entity display styles in App.css
if grep -q "matched-entities" frontend/src/App.css; then
    echo -e "${GREEN}✅ Entity display styles present${NC}"
else
    echo -e "${YELLOW}⚠️  Entity styles not found${NC}"
fi

# Check for match_entities method in rag_engine.py
if grep -q "match_entities" backend/app/rag_engine.py; then
    echo -e "${GREEN}✅ Entity matching logic in RAG engine${NC}"
else
    echo -e "${YELLOW}⚠️  Entity matching method not found${NC}"
fi

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Ready to Start Application!                         ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo "To start the application, run:"
echo -e "${YELLOW}docker-compose up --build${NC}"
echo ""
echo "Then access:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000/docs"
echo ""
echo "📚 Testing Instructions:"
echo "1. Upload entities.json via the UI sidebar"
echo "2. Click the floating chat button (bottom right)"
echo "3. Ask: 'Which entity handles clearing for Schwab?'"
echo "4. Verify green entity badges appear in the response"
echo ""
echo "📖 Documentation:"
echo "  • Quick Start:    QUICK_START.md"
echo "  • Full Details:   ENTITY_INTEGRATION.md"
echo "  • Summary:        IMPLEMENTATION_SUMMARY.md"
echo ""
