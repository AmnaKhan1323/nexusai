"""
NexusAI — RAG Pipeline Tests
Unit tests for the RAG service, context building, and prompt engineering.
"""

import pytest
from unittest.mock import MagicMock, patch
from services.rag_service import RAGService


class TestRAGService:
    """Test suite for the RAGService."""

    def setup_method(self):
        """Set up test fixtures with mocked dependencies."""
        with patch("services.rag_service.ollama_client"), \
             patch("services.rag_service.EmbeddingService"), \
             patch("services.rag_service.VectorStoreService"):
            self.service = RAGService()

        self.service.embedding_service = MagicMock()
        self.service.vector_store = MagicMock()

    def _make_search_results(self, count: int = 3, base_score: float = 0.9):
        """Generate mock search results."""
        results = []
        for i in range(count):
            results.append({
                "id": f"doc1_{i}",
                "score": base_score - (i * 0.05),
                "metadata": {
                    "document_id": "doc-001",
                    "document_name": f"test_document_{i}.pdf",
                    "chunk_index": i,
                    "content": f"This is test content for chunk {i}. It contains important information about topic {i}.",
                    "token_count": 20,
                },
            })
        return results

    def test_build_context_respects_token_limit(self):
        """Context builder should not exceed the max token budget."""
        self.service.max_context_tokens = 50

        results = self._make_search_results(count=10)
        context = self.service._build_context(results)

        total_content = " ".join(c["content"] for c in context)
        from utils.helpers import count_tokens
        total_tokens = count_tokens(total_content)

        assert total_tokens <= self.service.max_context_tokens + 20

    def test_build_context_preserves_order(self):
        """Context chunks should maintain the same order as search results (by relevance)."""
        results = self._make_search_results(count=5)
        context = self.service._build_context(results)

        for i in range(1, len(context)):
            assert context[i - 1]["score"] >= context[i]["score"]

    def test_format_context_includes_source_labels(self):
        """Formatted context should include [Source N] labels for each chunk."""
        results = self._make_search_results(count=3)
        context = self.service._build_context(results)
        formatted = self.service._format_context(context)

        assert "[Source 1]" in formatted
        assert "[Source 2]" in formatted
        assert "[Source 3]" in formatted

    def test_format_context_includes_document_names(self):
        """Formatted context should reference the source document name."""
        results = self._make_search_results(count=2)
        context = self.service._build_context(results)
        formatted = self.service._format_context(context)

        assert "test_document_0.pdf" in formatted
        assert "test_document_1.pdf" in formatted

    def test_build_user_prompt_structure(self):
        """User prompt should contain the question and context."""
        question = "What is the revenue growth?"
        context = "Revenue grew by 23% year over year."

        prompt = self.service._build_user_prompt(question, context)

        assert question in prompt
        assert context in prompt
        assert "CONTEXT FROM DOCUMENTS" in prompt
        assert "USER QUESTION" in prompt

    def test_extract_citations_structure(self):
        """Citations should have the required fields."""
        results = self._make_search_results(count=3)
        context = self.service._build_context(results)
        citations = self.service._extract_citations(results, context)

        assert len(citations) == 3
        for citation in citations:
            assert "document_name" in citation
            assert "document_id" in citation
            assert "chunk_index" in citation
            assert "content" in citation
            assert "relevance_score" in citation

    def test_extract_citations_scores_valid(self):
        """Citation relevance scores should be between 0 and 1."""
        results = self._make_search_results(count=3)
        context = self.service._build_context(results)
        citations = self.service._extract_citations(results, context)

        for citation in citations:
            assert 0.0 <= citation["relevance_score"] <= 1.0

    def test_generate_answer_no_results(self):
        """When no relevant documents are found, return a helpful message."""
        self.service.embedding_service.generate_embedding.return_value = [0.0] * 768
        self.service.vector_store.search.return_value = []

        result = self.service.generate_answer("What is the meaning of life?")

        assert "couldn't find" in result["answer"].lower() or "no relevant" in result["answer"].lower()
        assert result["citations"] == []
        assert result["tokens_used"] == 0

    @patch("services.rag_service.ollama_client")
    def test_generate_answer_with_results(self, mock_ollama):
        """Full pipeline should return answer with citations when results are found."""
        self.service.embedding_service.generate_embedding.return_value = [0.1] * 768
        self.service.vector_store.search.return_value = self._make_search_results(count=2)

        mock_ollama.chat.return_value = {
            "message": {"content": "The revenue grew by 23% [Source 1]."},
            "eval_count": 100,
            "prompt_eval_count": 50,
        }

        result = self.service.generate_answer("What was the revenue growth?")

        assert result["answer"] == "The revenue grew by 23% [Source 1]."
        assert len(result["citations"]) == 2
        assert result["tokens_used"] == 150

    @patch("services.rag_service.ollama_client")
    def test_generate_answer_llm_failure(self, mock_ollama):
        """LLM failure should raise a RuntimeError."""
        self.service.embedding_service.generate_embedding.return_value = [0.1] * 768
        self.service.vector_store.search.return_value = self._make_search_results(count=1)

        mock_ollama.chat.side_effect = Exception("Connection refused")

        with pytest.raises(RuntimeError, match="LLM generation failed"):
            self.service.generate_answer("Test question?")

    def test_citation_content_truncated(self):
        """Citation content should be truncated to max 500 characters."""
        long_content = "A" * 1000
        results = [{
            "id": "doc1_0",
            "score": 0.95,
            "metadata": {
                "document_id": "doc-001",
                "document_name": "long_doc.pdf",
                "chunk_index": 0,
                "content": long_content,
                "token_count": 200,
            },
        }]

        context = self.service._build_context(results)
        citations = self.service._extract_citations(results, context)

        assert len(citations[0]["content"]) <= 500
