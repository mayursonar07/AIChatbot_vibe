# AI RAG Chatbot - Copilot Instructions

## Architecture Overview

This is a **containerized RAG (Retrieval-Augmented Generation) chatbot** with a React TypeScript frontend and Python FastAPI backend. The system uses LangChain for RAG orchestration, ChromaDB for vector storage, and OpenAI for embeddings/LLM.

### Service Boundaries
- **Frontend** (`frontend/`): React 19 + TypeScript, runs on port 3000 (nginx in production)
- **Backend** (`backend/`): FastAPI + LangChain, runs on port 8000 with uvicorn
- **Communication**: HTTP REST API, CORS enabled for localhost development
- **Network**: Both services run in `rag-network` Docker network, frontend depends on backend

### Key Data Flows
1. **Document Upload**: Frontend → `/api/upload` → `rag_engine.process_document()` → Text splitting → Vector embedding → ChromaDB persistence
2. **Chat Query**: Frontend → `/api/chat` → `rag_engine.chat()` → (Optional) Vector retrieval → LLM augmentation → Response with sources
3. **State Management**: Conversation memory stored in-memory (dict by session_id), vector DB persisted to `/app/vector_db`

## Critical Developer Workflows

### Starting the Application
```bash
# IMPORTANT: Docker Desktop must be running first
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

### Hot Reload in Docker
Both services support hot reload via volume mounts:
- Frontend: `./frontend/src:/app/src` (React hot reload with CHOKIDAR_USEPOLLING=true)
- Backend: `./backend/app:/app/app` (uvicorn --reload flag)

### Dependency Management
**Backend**: Never use exact version pins for langchain packages - use `>=` to avoid conflicts:
```bash
# ❌ Wrong: langchain-openai==0.0.2
# ✅ Right: langchain-openai>=0.1.0
```
- Recent fix: `anthropic>=0.17.0` required by `langchain-anthropic 0.1.1`
- OpenAI SDK initialization changed: use `api_key=` not `openai_api_key=`

**Frontend**: Standard React setup, npm manages dependencies inside container

### Environment Variables
**Critical**: `.env` files are gitignored (security). Three locations:
- Root `.env`: Loaded by docker-compose, contains `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
- `backend/.env`: Backup location for local dev
- `frontend/.env`: Contains `REACT_APP_API_URL` (defaults to localhost:8000)

## Project-Specific Conventions

### Backend Structure (`backend/app/`)
- `main.py`: FastAPI app with global `rag_engine` initialized at startup, exposes `/api/chat` and `/api/upload` endpoints
- `models.py`: Pydantic models for request/response validation (ChatRequest with session_id, ChatResponse with response field, DocumentUploadResponse with file_id, SourceDocument)
- `rag_engine.py`: Core RAG logic - single `RAGEngine` class handles embeddings, LLM, vector store, and conversation memory

### Frontend Patterns
- **API Communication**: Axios for all HTTP requests, base URL from env var
- **TypeScript Interfaces**: Strict typing for Message, SourceDocument, UploadedFile
- **State Management**: React hooks only (useState, useEffect, useRef)
- **UI Components**: Lucide-react for icons, inline CSS in App.css (glassmorphism design)

### RAG Engine Specifics
- **Vector Store**: ChromaDB with persistence to `/app/vector_db`, collection name "rag_documents"
- **Chunking Strategy**: RecursiveCharacterTextSplitter (chunk_size=1000, overlap=200)
- **Retrieval**: Top-3 similar chunks (k=3) via vector similarity search
- **Memory**: ConversationalRetrievalChain with ConversationBufferMemory per session_id
- **Supported Formats**: PDF (PyPDFLoader), TXT (TextLoader), DOCX (Docx2txtLoader), PPTX (UnstructuredPowerPointLoader), XLSX (UnstructuredExcelLoader)
- **Embeddings**: OpenAI text-embedding-ada-002
- **LLM**: gpt-3.5-turbo with temperature=0.7

### Docker Conventions
- **Multi-stage builds**: Frontend has dev/build/production stages
- **Health checks**: Backend includes curl-based health check at `/health`
- **Volume strategy**: Persistent data (uploads, vector_db) mounted from host
- **Container names**: `rag-chatbot-frontend`, `rag-chatbot-backend`

## Integration Points

### External Dependencies
- **OpenAI API**: Required for embeddings (text-embedding-ada-002) and LLM (gpt-3.5-turbo)
- **Optional**: Anthropic API for Claude models (configured but not actively used)

### Cross-Component Communication
- **API Contract**: Frontend expects specific response structure:
  - Chat POST `/api/chat`: Request `{message, session_id, use_rag}` → Response `{response, timestamp, sources[]}`
  - Upload POST `/api/upload`: Multipart file → Response `{success, message, file_id, filename, chunks_created}`
  - Sources array contains: `{content, filename, page?, relevance_score}`
- **Error Handling**: Backend raises HTTPException with detail messages, frontend shows notifications with 5s auto-dismiss
- **Session Management**: Frontend generates `session_${Date.now()}` and maintains it for conversation context throughout the chat session

## Common Pitfalls & Solutions

1. **"Error loading ASGI app"**: Means `app.main:app` not found - check `main.py` has `app = FastAPI()` at module level
2. **OpenAI validation errors**: Use `api_key=` parameter, not `openai_api_key=` (newer SDK versions)
3. **Version conflicts**: LangChain packages have tight interdependencies - use `>=` constraints
4. **RAG not initializing**: Check OPENAI_API_KEY is set and docker-compose passes it via environment block
5. **Frontend can't reach backend**: Ensure `depends_on: backend` in docker-compose and both in same network
6. **Wrong API endpoints**: Frontend uses `/api/chat` and `/api/upload`, not `/chat` and `/upload`
7. **Response field mismatch**: ChatResponse must use `response` field, not `message` - critical for frontend parsing
8. **PPTX/XLSX support**: Requires `unstructured` library with extras - ensure `unstructured[pptx]` and `unstructured[xlsx]` in requirements.txt
9. **Session vs Conversation ID**: Backend uses `session_id` parameter, not `conversation_id` - must match frontend expectations

## File References
- Core API routes: `backend/app/main.py` - FastAPI endpoints at `/api/chat`, `/api/upload`, `/api/stats`, `/health`
- RAG implementation: `backend/app/rag_engine.py` - RAGEngine class with chat(), process_document(), get_vector_store_stats()
- Data models: `backend/app/models.py` - ChatRequest, ChatResponse, DocumentUploadResponse, SourceDocument
- Frontend chat logic: `frontend/src/App.tsx` - handleSendMessage, handleFileUpload functions
- Docker orchestration: `docker-compose.yml` - defines service dependencies and volumes
- Dependencies: `backend/requirements.txt` - includes unstructured library for PPTX/XLSX support

## Key Implementation Details

### Chat Response Structure
```python
ChatResponse(
    response: str,              # Main response text (NOT "message")
    timestamp: str,             # ISO format timestamp
    sources: List[SourceDocument]  # Optional source documents
)
```

### Source Document Structure
```python
SourceDocument(
    content: str,               # Excerpt from source (truncated to 300 chars)
    filename: str,              # Original filename
    page: Optional[int],        # Page number for PDFs (1-indexed)
    relevance_score: float      # Vector similarity score
)
```

### Document Processing Flow
1. File uploaded via multipart/form-data to `/api/upload`
2. File saved to `/app/uploads` directory
3. Appropriate loader selected based on extension (PDF/TXT/DOCX/PPTX/XLSX)
4. Document split into chunks with RecursiveCharacterTextSplitter
5. Metadata added: file_id, filename, upload_date, chunk_index, total_chunks
6. Chunks embedded and stored in ChromaDB
7. Response returns file_id, filename, chunks_created count

### RAG Modes
- **RAG ON + Documents**: Uses ConversationalRetrievalChain with vector retrieval
- **RAG ON + No Documents**: Returns helpful message prompting user to upload documents
- **RAG OFF**: Direct LLM chat with conversation memory maintained
