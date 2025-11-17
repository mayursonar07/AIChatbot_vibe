"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for conversation context")
    use_rag: bool = Field(True, description="Whether to use RAG for this query")


class SourceDocument(BaseModel):
    """Source document model for RAG responses"""
    content: str = Field(..., description="Excerpt from the source document")
    filename: str = Field(..., description="Name of the source file")
    page: Optional[int] = Field(None, description="Page number (for PDFs)")
    relevance_score: float = Field(..., description="Relevance score from vector search")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str = Field(..., description="Assistant response message")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    sources: Optional[List[SourceDocument]] = Field(default=[], description="Source documents used in RAG")


class DocumentUploadResponse(BaseModel):
    """Response model for document upload"""
    success: bool = Field(..., description="Whether upload was successful")
    message: str = Field(..., description="Status message")
    file_id: Optional[str] = Field(None, description="Unique identifier for the uploaded file")
    filename: Optional[str] = Field(None, description="Name of the uploaded file")
    chunks_created: Optional[int] = Field(None, description="Number of text chunks created")