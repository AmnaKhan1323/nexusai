"""
NexusAI — Pydantic Schemas
Request/response models for API validation and serialization.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Citations ──────────────────────────────────────────────

class Citation(BaseModel):
    document_name: str
    document_id: str
    chunk_index: int
    content: str
    relevance_score: float = Field(ge=0.0, le=1.0)
    page_number: Optional[int] = None


# ── Documents ──────────────────────────────────────────────

class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    status: str
    message: str

    class Config:
        from_attributes = True


class DocumentResponse(BaseModel):
    id: str
    filename: str
    file_type: str
    file_size: int
    upload_date: datetime
    chunk_count: int
    total_tokens: int
    status: str

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


class ChunkResponse(BaseModel):
    id: str
    chunk_index: int
    content: str
    token_count: int
    page_number: Optional[int] = None

    class Config:
        from_attributes = True


class DocumentChunksResponse(BaseModel):
    document_id: str
    filename: str
    chunks: List[ChunkResponse]
    total_chunks: int


# ── Chat ───────────────────────────────────────────────────

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000)
    session_id: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)


class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    session_id: str
    tokens_used: int


class ChatMessageResponse(BaseModel):
    id: str
    role: str
    content: str
    citations: Optional[List[Citation]] = None
    tokens_used: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    message_count: int = 0

    class Config:
        from_attributes = True


class ChatSessionListResponse(BaseModel):
    sessions: List[ChatSessionResponse]
    total: int


class ChatMessagesListResponse(BaseModel):
    session_id: str
    messages: List[ChatMessageResponse]
    total: int


# ── Error ──────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    error_code: Optional[str] = None
