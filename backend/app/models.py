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


class EntityMatchRequest(BaseModel):
    """Request model for entity matching"""
    query: str = Field(..., description="User query to match against entities")
    session_id: Optional[str] = Field(None, description="Session ID for context")


class EntityMatch(BaseModel):
    """Model for a matched entity"""
    name: str = Field(..., description="Entity name")
    shortCode: str = Field(..., description="Entity short code")
    category: str = Field(..., description="Entity category")
    confidence: float = Field(..., description="Match confidence score")


class EntityMatchResponse(BaseModel):
    """Response model for entity matching"""
    matches: List[EntityMatch] = Field(..., description="List of matched entities")
    explanation: str = Field(..., description="AI explanation of the matches")


class TextIngestionRequest(BaseModel):
    """Request model for direct text/data ingestion"""
    content: str = Field(..., description="Text content or JSON string to ingest")
    metadata: Optional[dict] = Field(default={}, description="Optional metadata (source, category, etc.)")
    document_name: Optional[str] = Field(default="api_document", description="Name for this document")


class TextIngestionResponse(BaseModel):
    """Response model for text ingestion"""
    success: bool = Field(..., description="Whether ingestion was successful")
    message: str = Field(..., description="Status message")
    document_id: str = Field(..., description="Unique identifier for the ingested document")
    chunks_created: int = Field(..., description="Number of text chunks created")


class DocumentUpdateRequest(BaseModel):
    """Request model for updating an existing document"""
    document_id: str = Field(..., description="ID of the document to update")
    content: str = Field(..., description="New content for the document")
    metadata: Optional[dict] = Field(default={}, description="Updated metadata")
    document_name: Optional[str] = Field(None, description="Updated document name")


class DocumentDeleteRequest(BaseModel):
    """Request model for deleting a document"""
    document_id: str = Field(..., description="ID of the document to delete")


class DocumentDeleteResponse(BaseModel):
    """Response model for document deletion"""
    success: bool = Field(..., description="Whether deletion was successful")
    message: str = Field(..., description="Status message")
    document_id: str = Field(..., description="ID of the deleted document")
    chunks_deleted: int = Field(..., description="Number of chunks deleted")
