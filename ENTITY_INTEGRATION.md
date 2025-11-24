# Entity Integration with RAG - Implementation Guide

## Overview
The chat slider is now fully integrated with the RAG backend, enabling intelligent entity matching and recommendations based on user queries.

## Features Implemented

### 1. **Real-time RAG Integration**
- Chat sidebar now connects to `/api/chat` endpoint instead of using mock responses
- Maintains session-based conversation context
- Supports both RAG-enabled and RAG-disabled modes
- Shows loading states during API calls

### 2. **Entity Matching & Display**
- Automatically detects entity names mentioned in AI responses
- Highlights matched entities in a dedicated section with:
  - Entity name (bold, green highlight)
  - Short code
  - Category
- Displays source documents when RAG retrieves information

### 3. **Enhanced Chat Experience**
- Messages include matched entities badges
- Source attribution when information comes from documents
- Real-time typing indicators
- Error handling with user-friendly messages

### 4. **Backend Entity Matching Endpoint**
- New `/api/match-entity` endpoint for dedicated entity matching
- Uses RAG to match user descriptions to exact entity names
- Returns confidence scores and explanations
- Supports both document-based and direct LLM matching

## How It Works

### Frontend Flow
1. User types query in chat sidebar
2. Frontend enhances query with entity context if entities.json not uploaded
3. Sends request to `/api/chat` with session ID and RAG mode
4. Receives response with:
   - AI-generated answer
   - Optional source documents
   - Timestamp
5. Frontend extracts entity names from response using regex matching
6. Displays matched entities in highlighted section

### Backend Flow
1. RAG engine receives chat request
2. If RAG enabled and entities.json uploaded:
   - Performs vector similarity search
   - Retrieves top 5 relevant chunks
   - Augments LLM prompt with context
3. LLM generates response mentioning specific entity names
4. Returns response with sources and metadata

## Usage Instructions

### For Users
1. **Upload entities.json**:
   - Click "Upload Document" in sidebar
   - Select `entities.json` file
   - Wait for "uploaded successfully" notification

2. **Ask About Entities**:
   - Click the floating chat button (bottom right)
   - Type queries like:
     - "Which entity handles clearing for Schwab?"
     - "I need a custodian entity"
     - "Show me entities for fund services"
   
3. **View Matched Entities**:
   - Matched entities appear in green highlighted boxes
   - Each shows: **Entity Name** (CODE) - Category
   - Click the entity to view more details (future enhancement)

### Example Queries
```
User: "I need a clearing house for Charles Schwab"
AI: "For Charles Schwab Corporation, the clearing operations are 
     handled by Schwab Clearing Services (SCS)."

Matched Entities:
✅ Schwab Clearing Services (SCS) - Clearing House
```

## API Endpoints

### POST /api/chat
**Request:**
```json
{
  "message": "Which entity handles custodian services for Fidelity?",
  "session_id": "session_1234567890",
  "use_rag": true
}
```

**Response:**
```json
{
  "response": "Fidelity Clearing & Custody (FCC) handles custody and clearing solutions...",
  "timestamp": "2024-11-24T10:30:00.000Z",
  "sources": [
    {
      "content": "Fidelity Clearing & Custody...",
      "filename": "entities.json",
      "relevance_score": 0.92
    }
  ]
}
```

### POST /api/match-entity
**Request:**
```json
{
  "query": "I need a custodian for institutional services",
  "session_id": "session_1234567890"
}
```

**Response:**
```json
{
  "matches": [
    {
      "name": "State Street Corporation",
      "shortCode": "STT",
      "category": "Custodian",
      "confidence": 0.95
    },
    {
      "name": "BNY Mellon Asset Servicing",
      "shortCode": "BNY",
      "category": "Custodian",
      "confidence": 0.88
    }
  ],
  "explanation": "Based on your query for institutional custodian services, State Street and BNY Mellon are the top matches..."
}
```

## Technical Implementation

### Frontend Changes
- **File**: `frontend/src/App.tsx`
  - Removed mock responses
  - Added `ChatSidebar` props: `useRag`, `uploadedFiles`
  - Implemented real API integration with axios
  - Added entity extraction logic using regex
  - Enhanced message interface with `sources` and `matchedEntities`

- **File**: `frontend/src/App.css`
  - Added `.matched-entities` styles (green theme)
  - Added `.message-sources` styles (blue theme)
  - Added loading states for disabled inputs
  - Responsive design for entity badges

### Backend Changes
- **File**: `backend/app/models.py`
  - Added `EntityMatchRequest` model
  - Added `EntityMatch` model
  - Added `EntityMatchResponse` model

- **File**: `backend/app/main.py`
  - Added `/api/match-entity` endpoint
  - Imported new models

- **File**: `backend/app/rag_engine.py`
  - Added `match_entities()` method
  - JSON parsing for entity extraction
  - Confidence scoring based on LLM analysis

## Configuration

### Environment Variables
No additional environment variables required. Uses existing:
- `OPENAI_API_KEY` - For embeddings and LLM
- `REACT_APP_API_URL` - Frontend API endpoint (defaults to localhost:8000)

### RAG Settings
Current configuration in `rag_engine.py`:
- **Chunk Size**: 1000 characters
- **Chunk Overlap**: 200 characters
- **Retrieval Count**: 5 documents (increased for better context)
- **LLM Model**: gpt-4o-mini
- **Temperature**: 0.7

## Testing

### Test Scenario 1: Entity Upload and Query
```bash
# 1. Start application
docker-compose up --build

# 2. Upload entities.json via UI
# 3. Open chat sidebar (click floating button)
# 4. Ask: "Which entity is a custodian?"
# Expected: Lists custodian entities with green badges
```

### Test Scenario 2: RAG Toggle
```bash
# 1. Toggle RAG OFF
# 2. Ask about entities
# Expected: General responses without document context

# 3. Toggle RAG ON
# 4. Ask same question
# Expected: Specific entity names from uploaded document
```

### Test Scenario 3: Session Persistence
```bash
# 1. Ask: "Tell me about Fidelity"
# 2. Ask: "What about their clearing services?"
# Expected: AI remembers context from previous message
```

## Future Enhancements

### Planned Features
1. **Click-to-Select Entity**: Click matched entity to auto-populate dropdown
2. **Entity Details Modal**: Show full entity info on hover/click
3. **Smart Suggestions**: Auto-suggest entities while typing in dropdowns
4. **Entity Comparison**: Compare multiple entities side-by-side
5. **Advanced Filtering**: Filter entities by category in chat
6. **Export Chat History**: Download conversation with entity recommendations

### Technical Improvements
1. **Caching**: Cache entity embeddings for faster retrieval
2. **Fuzzy Matching**: Handle typos and variations in entity names
3. **Analytics**: Track which entities are queried most
4. **Multi-language**: Support entity matching in multiple languages

## Troubleshooting

### Issue: Entities not detected
**Solution**: Ensure entities.json is uploaded and contains all fields (name, shortCode, category, description)

### Issue: No RAG responses
**Solution**: 
1. Check OPENAI_API_KEY is set
2. Verify docker-compose passes environment variables
3. Check backend logs for initialization errors

### Issue: Chat not connecting
**Solution**:
1. Verify backend is running on port 8000
2. Check CORS settings in main.py
3. Inspect browser console for network errors

## Support
For issues or questions, check:
- Backend logs: `docker logs rag-chatbot-backend`
- Frontend logs: Browser DevTools Console
- API docs: http://localhost:8000/docs
