"""
NexusAI — Document Router
Handles document upload, listing, retrieval, deletion, and chunk access.
"""

import logging
import os
import uuid
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from config import settings
from database.connection import get_db
from database.models import Document, DocumentChunk
from models.schemas import (
    DocumentUploadResponse,
    DocumentResponse,
    DocumentListResponse,
    DocumentChunksResponse,
    ChunkResponse,
)
from services.document_processor import DocumentProcessor
from services.chunking import ChunkingService
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStoreService

logger = logging.getLogger("nexusai.documents")

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".docx"}


def _validate_file(file: UploadFile) -> str:
    """Validate uploaded file type and size."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided.")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
        )
    return ext


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a PDF or DOCX document for processing."""
    ext = _validate_file(file)

    file_content = await file.read()
    file_size = len(file_content)

    if file_size > settings.max_file_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"File exceeds maximum size of {settings.max_file_size_mb}MB.",
        )

    doc_id = str(uuid.uuid4())
    save_path = os.path.join(settings.upload_dir, f"{doc_id}{ext}")
    os.makedirs(settings.upload_dir, exist_ok=True)

    with open(save_path, "wb") as f:
        f.write(file_content)

    doc = Document(
        id=doc_id,
        filename=file.filename,
        file_type=ext.replace(".", ""),
        file_size=file_size,
        status="processing",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    logger.info(f"📄 Document uploaded: {file.filename} ({doc_id})")

    try:
        processor = DocumentProcessor()
        raw_text = processor.extract_text(save_path, ext)

        if not raw_text.strip():
            doc.status = "failed"
            db.commit()
            raise HTTPException(status_code=422, detail="Could not extract text from the document.")

        chunking_service = ChunkingService(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )
        chunks = chunking_service.chunk_text(raw_text)

        embedding_service = EmbeddingService()
        texts = [c["content"] for c in chunks]
        embeddings = embedding_service.generate_embeddings(texts)

        vector_store = VectorStoreService()
        vectors_to_upsert = []

        total_tokens = 0
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = str(uuid.uuid4())
            embedding_id = f"{doc_id}_{i}"

            db_chunk = DocumentChunk(
                id=chunk_id,
                document_id=doc_id,
                chunk_index=i,
                content=chunk["content"],
                embedding_id=embedding_id,
                token_count=chunk["token_count"],
                page_number=chunk.get("page_number"),
            )
            db.add(db_chunk)
            total_tokens += chunk["token_count"]

            vectors_to_upsert.append({
                "id": embedding_id,
                "values": embedding,
                "metadata": {
                    "document_id": doc_id,
                    "document_name": file.filename,
                    "chunk_index": i,
                    "content": chunk["content"][:1000],
                    "token_count": chunk["token_count"],
                },
            })

        vector_store.upsert_vectors(vectors_to_upsert)

        doc.chunk_count = len(chunks)
        doc.total_tokens = total_tokens
        doc.status = "ready"
        db.commit()

        logger.info(f"✅ Document processed: {file.filename} → {len(chunks)} chunks, {total_tokens} tokens")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Processing failed for {file.filename}: {str(e)}")
        doc.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

    return DocumentUploadResponse(
        id=doc.id,
        filename=doc.filename,
        file_type=doc.file_type,
        file_size=doc.file_size,
        status=doc.status,
        message=f"Document processed successfully. {doc.chunk_count} chunks created.",
    )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents."""
    documents = db.query(Document).order_by(Document.upload_date.desc()).all()
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents],
        total=len(documents),
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db: Session = Depends(get_db)):
    """Get a specific document by ID."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")
    return DocumentResponse.model_validate(doc)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, db: Session = Depends(get_db)):
    """Delete a document and all associated chunks and vectors."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    try:
        vector_store = VectorStoreService()
        chunk_ids = [
            f"{document_id}_{i}" for i in range(doc.chunk_count)
        ]
        if chunk_ids:
            vector_store.delete_vectors(chunk_ids)
    except Exception as e:
        logger.warning(f"⚠️ Failed to delete vectors for {document_id}: {e}")

    file_path = os.path.join(settings.upload_dir, f"{document_id}.{doc.file_type}")
    if os.path.exists(file_path):
        os.remove(file_path)

    db.delete(doc)
    db.commit()
    logger.info(f"🗑️ Document deleted: {doc.filename} ({document_id})")


@router.get("/{document_id}/chunks", response_model=DocumentChunksResponse)
async def get_document_chunks(document_id: str, db: Session = Depends(get_db)):
    """Get all chunks for a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    chunks = (
        db.query(DocumentChunk)
        .filter(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
        .all()
    )

    return DocumentChunksResponse(
        document_id=doc.id,
        filename=doc.filename,
        chunks=[ChunkResponse.model_validate(c) for c in chunks],
        total_chunks=len(chunks),
    )
