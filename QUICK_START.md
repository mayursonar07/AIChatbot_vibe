# Quick Start Guide - Entity-Enhanced RAG Chatbot

## 🚀 Start the Application

```bash
# Ensure Docker Desktop is running, then:
docker-compose up --build
```

Access:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

## 📋 How to Use Entity Assistance

### Step 1: Upload Entity Data
1. In the sidebar, click **"Upload Document"**
2. Select `frontend/src/data/entities.json`
3. Wait for confirmation: "entities.json uploaded successfully!"

### Step 2: Ask About Entities
1. Click the **floating chat button** (bottom right, purple circle with message icon)
2. Type questions like:
   - "Which entity handles clearing for Schwab?"
   - "I need a custodian"
   - "Show me fund services entities"

### Step 3: View Results
The AI will respond with:
- **Text Answer**: Natural language explanation
- **✅ Matched Entities**: Green-highlighted boxes showing:
  - **Entity Name** (SHORT_CODE) - Category
- **📚 Sources**: Documents used (if RAG is ON)

## 💡 Example Conversation

```
You: I need a clearing house for Charles Schwab

AI: The clearing house for Charles Schwab Corporation is 
Schwab Clearing Services (SCS), which handles all clearing 
and settlement operations.

✅ Matched Entities:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
│ Schwab Clearing Services (SCS) - Clearing House │
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📚 Sources:
• entities.json (Score: 0.92)
```

## 🎛️ RAG Toggle

**RAG ON** (with documents uploaded):
- Uses uploaded entities.json
- Provides specific entity names
- Shows source attribution

**RAG OFF**:
- Direct LLM responses
- General knowledge only
- No source documents

## 🔍 Entity List in entities.json

Current entities (10 total):
1. **Charles Schwab Corporation** (SCHW) - Custodian
2. **Schwab Clearing Services** (SCS) - Clearing House
3. **Fidelity Investments** (FID) - Custodian
4. **Fidelity Clearing & Custody** (FCC) - Clearing House
5. **Vanguard Group** (VAN) - Fund Services
6. **BlackRock Fund Services** (BFS) - Fund Services
7. **State Street Corporation** (STT) - Custodian
8. **BNY Mellon Asset Servicing** (BNY) - Custodian
9. **Northern Trust Securities** (NTS) - Custodian
10. **Goldman Sachs Custody** (GSC) - Custodian

## 🛠️ Key Features

✅ **Real-time RAG Integration**
- Chat connects to FastAPI backend
- Session-based conversation memory
- Streaming-like response with loading states

✅ **Smart Entity Detection**
- Automatically finds entity names in responses
- Highlights matched entities in green
- Shows short codes and categories

✅ **Source Attribution**
- Displays documents used for answers
- Relevance scores for each source
- Clickable source previews

✅ **Context Awareness**
- Maintains conversation history
- Understands follow-up questions
- References previous entities mentioned

## 🧪 Testing Checklist

- [ ] Start Docker containers successfully
- [ ] Upload entities.json (sidebar → Upload Document)
- [ ] See "10 chunks" confirmation
- [ ] Open chat (click floating button)
- [ ] Ask: "Tell me about Fidelity entities"
- [ ] Verify green entity badges appear
- [ ] Check RAG ON/OFF toggle works
- [ ] Test follow-up question: "What about their clearing?"

## 🐛 Common Issues

### Chat not responding?
- Check backend logs: `docker logs rag-chatbot-backend`
- Verify OPENAI_API_KEY in `.env` file
- Restart containers: `docker-compose restart`

### Entities not highlighted?
- Ensure entities.json uploaded successfully
- Check entity names match exactly (case-insensitive)
- Try rephrasing query to include entity names

### No source documents showing?
- Toggle RAG ON (button in header)
- Re-upload entities.json
- Check vector_db has data: backend logs show "Vector store loaded with X chunks"

## 📝 Development Notes

**Modified Files:**
- `frontend/src/App.tsx` - Added RAG integration, entity matching
- `frontend/src/App.css` - Styles for matched entities & sources
- `backend/app/models.py` - New entity matching models
- `backend/app/main.py` - Added `/api/match-entity` endpoint
- `backend/app/rag_engine.py` - Added `match_entities()` method

**No Changes Needed:**
- `.env` file (already has OPENAI_API_KEY)
- `docker-compose.yml` (already configured)
- Database schema (uses existing ChromaDB)

## 🎯 Next Steps

1. **Test with your own entity data**
   - Update `frontend/src/data/entities.json`
   - Add more entities, categories, descriptions
   - Re-upload to test

2. **Enhance the prompt**
   - Modify `enhanced_message` in App.tsx
   - Add more context about entity types
   - Include business rules

3. **Add click-to-select**
   - Click matched entity to populate "Transfer From/To" dropdowns
   - Auto-fill form based on AI recommendations

## 📚 Documentation

- Full details: `ENTITY_INTEGRATION.md`
- Original README: `README.md`
- Copilot instructions: `.github/copilot-instructions.md`

---

**Ready to go!** Start Docker, upload entities.json, and start chatting! 🎉
