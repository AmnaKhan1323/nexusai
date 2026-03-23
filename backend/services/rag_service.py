"""
NexusAI — RAG Service
Full Retrieval-Augmented Generation pipeline using Ollama (100% FREE):
Query → Embed → Search ChromaDB → Context → Ollama LLM → Citations
"""

import logging
from typing import Any, Dict, List

import ollama as ollama_client

from config import settings
from services.embedding_service import EmbeddingService
from services.vector_store import VectorStoreService
from utils.helpers import count_tokens, truncate_text

logger = logging.getLogger("nexusai.rag")

SYSTEM_PROMPT = """You are NexusAI, an advanced document intelligence assistant. Your role is to provide accurate, well-structured answers based ONLY on the provided document context.

INSTRUCTIONS:
1. Answer the user's question using ONLY the information from the provided context chunks.
2. If the context does not contain enough information to fully answer the question, clearly state what information is available and what is missing.
3. NEVER fabricate or hallucinate information not present in the context.
4. When referencing information, cite the source using [Source N] notation, where N corresponds to the chunk number.
5. Structure your answers clearly with paragraphs, bullet points, or numbered lists as appropriate.
6. Be concise but thorough — provide complete answers without unnecessary verbosity.
7. If multiple sources provide related information, synthesize them into a coherent answer.

FORMATTING:
- Use Markdown formatting for readability.
- Use **bold** for key terms and important points.
- Use bullet points for lists of items.
- Include [Source N] citations inline where you reference specific information.
"""


class RAGService:
    """Orchestrates the full RAG pipeline for question answering using Ollama (free)."""

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStoreService()
        self.model = settings.llm_model
        self.max_context_tokens = settings.max_context_tokens
        self.temperature = settings.temperature

    def generate_answer(
        self,
        question: str,
        top_k: int = 5,
        score_threshold: float = 0.7,
    ) -> Dict[str, Any]:
        """Execute the full RAG pipeline.

        Args:
            question: The user's natural language question.
            top_k: Number of relevant chunks to retrieve.
            score_threshold: Minimum relevance score for retrieved chunks.

        Returns:
            Dict with keys: answer, citations, tokens_used.
        """
        logger.info(f"🔄 RAG Pipeline started for: '{question[:80]}...'")

        # Step 1: Embed the query
        query_embedding = self.embedding_service.generate_embedding(question)
        logger.info("✅ Query embedded via Ollama")

        # Step 2: Search ChromaDB for relevant chunks
        search_results = self.vector_store.search(
            query_vector=query_embedding,
            top_k=top_k,
            score_threshold=score_threshold,
        )

        if not search_results:
            logger.warning("⚠️ No relevant documents found")
            return {
                "answer": (
                    "I couldn't find any relevant information in the uploaded documents "
                    "to answer your question. Please make sure you've uploaded documents "
                    "related to your query, or try rephrasing your question."
                ),
                "citations": [],
                "tokens_used": 0,
            }

        # Step 3: Build context from retrieved chunks
        context_chunks = self._build_context(search_results)
        logger.info(f"📋 Context built from {len(context_chunks)} chunks")

        # Step 4: Format context and build prompt
        context_text = self._format_context(context_chunks)
        user_prompt = self._build_user_prompt(question, context_text)

        # Step 5: Call Ollama LLM
        answer, tokens_used = self._call_llm(user_prompt)
        logger.info(f"✅ Ollama response generated ({tokens_used} tokens)")

        # Step 6: Extract citations
        citations = self._extract_citations(search_results, context_chunks)

        return {
            "answer": answer,
            "citations": citations,
            "tokens_used": tokens_used,
        }

    def _build_context(self, search_results: List[Dict]) -> List[Dict]:
        """Build context from search results, respecting token limits."""
        context_chunks = []
        total_tokens = 0

        for result in search_results:
            metadata = result.get("metadata", {})
            content = metadata.get("content", "")
            chunk_tokens = count_tokens(content)

            if total_tokens + chunk_tokens > self.max_context_tokens:
                remaining_budget = self.max_context_tokens - total_tokens
                if remaining_budget > 50:
                    content = truncate_text(content, remaining_budget)
                    chunk_tokens = count_tokens(content)
                else:
                    break

            context_chunks.append({
                "content": content,
                "document_name": metadata.get("document_name", "Unknown"),
                "document_id": metadata.get("document_id", ""),
                "chunk_index": metadata.get("chunk_index", 0),
                "score": result.get("score", 0.0),
                "token_count": chunk_tokens,
            })
            total_tokens += chunk_tokens

        return context_chunks

    def _format_context(self, chunks: List[Dict]) -> str:
        """Format context chunks into a structured text block for the prompt."""
        context_parts = []

        for i, chunk in enumerate(chunks):
            source_label = f"[Source {i + 1}] (from: {chunk['document_name']}, relevance: {chunk['score']:.2f})"
            context_parts.append(f"{source_label}\n{chunk['content']}")

        return "\n\n---\n\n".join(context_parts)

    def _build_user_prompt(self, question: str, context: str) -> str:
        """Construct the user prompt with context and question."""
        return (
            f"CONTEXT FROM DOCUMENTS:\n"
            f"{'=' * 50}\n"
            f"{context}\n"
            f"{'=' * 50}\n\n"
            f"USER QUESTION: {question}\n\n"
            f"Please provide a comprehensive answer based on the context above. "
            f"Include [Source N] citations for key facts."
        )

    def _call_llm(self, user_prompt: str) -> tuple:
        """Call Ollama local LLM with the system and user prompts.

        Returns:
            Tuple of (answer_text, tokens_used).
        """
        try:
            response = ollama_client.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": self.temperature,
                    "num_predict": 1500,
                    "top_p": 0.95,
                },
            )

            answer = response["message"]["content"].strip()

            # Ollama provides token counts in the response
            tokens_used = (
                response.get("eval_count", 0)
                + response.get("prompt_eval_count", 0)
            )

            return answer, tokens_used

        except Exception as e:
            logger.error(f"❌ Ollama LLM call failed: {str(e)}")
            raise RuntimeError(
                f"LLM generation failed: {str(e)}. "
                f"Make sure Ollama is running (ollama serve) and model '{self.model}' is pulled (ollama pull {self.model})."
            )

    def _extract_citations(
        self,
        search_results: List[Dict],
        context_chunks: List[Dict],
    ) -> List[Dict]:
        """Build citation objects from the retrieved context chunks."""
        citations = []

        for i, chunk in enumerate(context_chunks):
            citations.append({
                "document_name": chunk["document_name"],
                "document_id": chunk["document_id"],
                "chunk_index": chunk["chunk_index"],
                "content": chunk["content"][:500],
                "relevance_score": round(chunk["score"], 4),
                "page_number": chunk.get("page_number"),
            })

        return citations
