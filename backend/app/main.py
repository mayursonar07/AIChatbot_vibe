"""
Main FastAPI application for RAG Chatbot
Provides REST API for document upload and conversational AI chat
"""
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

from app.rag_engine import RAGEngine
from app.models import (
    ChatRequest, 
    ChatResponse, 
    DocumentUploadResponse, 
    EntityMatchRequest, 
    EntityMatchResponse,
    TextIngestionRequest,
    TextIngestionResponse,
    DocumentUpdateRequest,
    DocumentDeleteRequest,
    DocumentDeleteResponse
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Chatbot API",
    description="AI-powered chatbot with Retrieval-Augmented Generation capabilities",
    version="1.0.0"
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global RAG engine instance
rag_engine: RAGEngine = None


@app.on_event("startup")
async def startup_event():
    """Initialize RAG engine on application startup"""
    global rag_engine
    try:
        rag_engine = RAGEngine()
        print("✅ RAG Engine initialized successfully")
        
        # Print vector store stats
        stats = rag_engine.get_vector_store_stats()
        print(f"📊 Vector Store: {stats}")
        
    except Exception as e:
        print(f"❌ Error initializing RAG Engine: {e}")
        raise


@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "message": "Welcome to RAG Chatbot API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "chat": "/api/chat",
            "upload": "/api/upload",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    if not rag_engine:
        return {
            "status": "unhealthy",
            "rag_engine": "not initialized"
        }
    
    stats = rag_engine.get_vector_store_stats()
    return {
        "status": "healthy",
        "rag_engine": "initialized",
        "vector_store": stats
    }


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint with RAG capabilities
    
    Processes user messages with optional document retrieval.
    Maintains conversation context per session.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check server logs."
        )
    
    try:
        response = await rag_engine.chat(
            message=request.message,
            session_id=request.session_id,
            use_rag=request.use_rag
        )
        return response
        
    except Exception as e:
        print(f"Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat request: {str(e)}"
        )


@app.post("/api/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Document upload endpoint
    
    Accepts various file formats (PDF, TXT, DOCX, PPTX, XLSX, JSON),
    processes them into chunks, and stores in vector database.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized. Please check server logs."
        )
    
    # Validate file type
    allowed_extensions = {'.pdf', '.txt', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', '.json'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_ext}. Allowed: {', '.join(allowed_extensions)}"
        )
    
    try:
        # Create uploads directory if it doesn't exist
        upload_dir = "/app/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Save uploaded file to disk
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        print(f"📄 Processing file: {file.filename} ({len(content)} bytes)")
        
        # Process document through RAG engine
        result = await rag_engine.process_document(
            file_path=file_path,
            filename=file.filename
        )
        
        # Clean up file after processing (optional)
        # os.remove(file_path)
        
        return result
        
    except Exception as e:
        print(f"Upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading document: {str(e)}"
        )


@app.post("/api/ingest", response_model=DocumentUploadResponse)
async def ingest_text(request: TextIngestionRequest):
    """
    Ingest raw text/JSON content directly into the knowledge base
    
    Accepts text or JSON data via API and creates embeddings without file upload.
    Useful for programmatically adding data to the RAG system.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    try:
        print(f"📝 Ingesting text document: {request.document_name}")
        print(f"📊 Content length: {len(request.content)} chars")
        
        # Process text through RAG engine
        result = await rag_engine.ingest_text(
            content=request.content,
            document_name=request.document_name,
            metadata=request.metadata or {}
        )
        
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
        
        return DocumentUploadResponse(
            success=result["success"],
            message=result["message"],
            file_id=result["document_id"],
            filename=request.document_name,
            chunks_created=result["chunks_created"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Ingestion error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error ingesting text: {str(e)}"
        )


@app.put("/api/document/{document_id}", response_model=DocumentUploadResponse)
async def update_document(document_id: str, request: DocumentUpdateRequest):
    """
    Update an existing document in the knowledge base
    
    Deletes old embeddings and creates new ones with updated content.
    Useful for keeping entity information fresh and avoiding stale data.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    # Validate document_id matches
    if document_id != request.document_id:
        raise HTTPException(
            status_code=400,
            detail="Document ID in URL and body must match"
        )
    
    try:
        print(f"📝 Updating document: {document_id}")
        
        result = await rag_engine.update_document(
            document_id=request.document_id,
            content=request.content,
            document_name=request.document_name,
            metadata=request.metadata or {}
        )
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return DocumentUploadResponse(
            success=result["success"],
            message=result["message"],
            file_id=result["document_id"],
            filename=request.document_name or "updated_document",
            chunks_created=result["chunks_created"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Update error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error updating document: {str(e)}"
        )


@app.delete("/api/document/{document_id}", response_model=DocumentDeleteResponse)
async def delete_document(document_id: str):
    """
    Delete a specific document from the knowledge base
    
    Removes all embeddings for this document. Use this when entities are
    deleted from your source system to keep the knowledge base in sync.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    try:
        print(f"🗑️  Deleting document: {document_id}")
        
        result = await rag_engine.delete_document(document_id)
        
        if not result["success"]:
            raise HTTPException(status_code=404, detail=result["message"])
        
        return DocumentDeleteResponse(
            success=result["success"],
            message=result["message"],
            document_id=result["document_id"],
            chunks_deleted=result["chunks_deleted"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Delete error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting document: {str(e)}"
        )


@app.get("/api/stats")
async def get_stats():
    """
    Get vector store statistics
    
    Returns information about indexed documents and chunks.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    try:
        stats = rag_engine.get_vector_store_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting stats: {str(e)}"
        )


@app.delete("/api/clear")
async def clear_knowledge_base():
    """
    Clear all documents from the knowledge base
    
    Deletes all uploaded documents and their embeddings from the vector store.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    try:
        result = rag_engine.clear_vector_store()
        if result["success"]:
            return result
        else:
            raise HTTPException(status_code=500, detail=result["message"])
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing knowledge base: {str(e)}"
        )


@app.post("/api/match-entity", response_model=EntityMatchResponse)
async def match_entity(request: EntityMatchRequest):
    """
    Entity matching endpoint using RAG
    
    Uses the uploaded entities.json and RAG to match user descriptions
    to exact entity names with confidence scores.
    """
    if not rag_engine:
        raise HTTPException(
            status_code=503,
            detail="RAG engine not initialized"
        )
    
    try:
        response = await rag_engine.match_entities(
            query=request.query,
            session_id=request.session_id
        )
        return response
    except Exception as e:
        print(f"Entity matching error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error matching entities: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
