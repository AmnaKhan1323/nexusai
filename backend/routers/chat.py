"""
NexusAI — Chat Router
Handles RAG-based question answering and chat session management.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from database.models import ChatSession, ChatMessage
from models.schemas import (
    ChatRequest,
    ChatResponse,
    ChatSessionResponse,
    ChatSessionListResponse,
    ChatMessageResponse,
    ChatMessagesListResponse,
    Citation,
)
from services.rag_service import RAGService

logger = logging.getLogger("nexusai.chat")

router = APIRouter()


@router.post("/ask", response_model=ChatResponse)
async def ask_question(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Ask a question using RAG pipeline. Returns answer with citations."""
    logger.info(f"💬 Question received: {request.question[:100]}...")

    if request.session_id:
        session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    else:
        title = request.question[:80] + ("..." if len(request.question) > 80 else "")
        session = ChatSession(title=title)
        db.add(session)
        db.commit()
        db.refresh(session)
        logger.info(f"📝 New chat session created: {session.id}")

    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=request.question,
    )
    db.add(user_message)
    db.commit()

    try:
        rag_service = RAGService()
        result = rag_service.generate_answer(
            question=request.question,
            top_k=request.top_k,
        )

        citations = [
            Citation(
                document_name=c["document_name"],
                document_id=c["document_id"],
                chunk_index=c["chunk_index"],
                content=c["content"],
                relevance_score=c["relevance_score"],
                page_number=c.get("page_number"),
            )
            for c in result["citations"]
        ]

        citation_dicts = [c.model_dump() for c in citations]

        assistant_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content=result["answer"],
            citations=citation_dicts,
            tokens_used=result.get("tokens_used", 0),
        )
        db.add(assistant_message)
        db.commit()

        logger.info(
            f"✅ Answer generated with {len(citations)} citations, "
            f"{result.get('tokens_used', 0)} tokens used"
        )

        return ChatResponse(
            answer=result["answer"],
            citations=citations,
            session_id=session.id,
            tokens_used=result.get("tokens_used", 0),
        )

    except Exception as e:
        logger.error(f"❌ RAG pipeline failed: {str(e)}")

        error_message = ChatMessage(
            session_id=session.id,
            role="assistant",
            content="I apologize, but I encountered an error while processing your question. Please try again.",
            citations=[],
            tokens_used=0,
        )
        db.add(error_message)
        db.commit()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate answer: {str(e)}",
        )


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_chat_sessions(db: Session = Depends(get_db)):
    """List all chat sessions, most recent first."""
    sessions = (
        db.query(ChatSession)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )

    session_responses = []
    for s in sessions:
        msg_count = db.query(ChatMessage).filter(ChatMessage.session_id == s.id).count()
        session_responses.append(
            ChatSessionResponse(
                id=s.id,
                title=s.title,
                created_at=s.created_at,
                updated_at=s.updated_at,
                message_count=msg_count,
            )
        )

    return ChatSessionListResponse(
        sessions=session_responses,
        total=len(session_responses),
    )


@router.get("/sessions/{session_id}/messages", response_model=ChatMessagesListResponse)
async def get_session_messages(session_id: str, db: Session = Depends(get_db)):
    """Get all messages in a chat session."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    messages = (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    message_responses = []
    for m in messages:
        citations = None
        if m.citations:
            citations = [Citation(**c) for c in m.citations]
        message_responses.append(
            ChatMessageResponse(
                id=m.id,
                role=m.role,
                content=m.content,
                citations=citations,
                tokens_used=m.tokens_used or 0,
                created_at=m.created_at,
            )
        )

    return ChatMessagesListResponse(
        session_id=session_id,
        messages=message_responses,
        total=len(message_responses),
    )


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_chat_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a chat session and all its messages."""
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    db.delete(session)
    db.commit()
    logger.info(f"🗑️ Chat session deleted: {session_id}")
