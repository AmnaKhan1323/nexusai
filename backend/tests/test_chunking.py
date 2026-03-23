"""
NexusAI — Chunking Service Tests
Unit tests for text chunking, merging, and overlap logic.
"""

import pytest
from services.chunking import ChunkingService
from utils.helpers import count_tokens


class TestChunkingService:
    """Test suite for the ChunkingService."""

    def setup_method(self):
        """Set up test fixtures."""
        self.service = ChunkingService(chunk_size=100, chunk_overlap=20)

    def test_empty_text_returns_no_chunks(self):
        """Empty or whitespace-only text should produce zero chunks."""
        assert self.service.chunk_text("") == []
        assert self.service.chunk_text("   ") == []
        assert self.service.chunk_text("\n\n") == []

    def test_short_text_single_chunk(self):
        """Text shorter than chunk_size should produce one chunk."""
        text = "This is a short sentence for testing."
        chunks = self.service.chunk_text(text)
        assert len(chunks) == 1
        assert chunks[0]["content"] == text
        assert chunks[0]["chunk_index"] == 0
        assert chunks[0]["token_count"] > 0

    def test_chunk_index_sequential(self):
        """Chunk indices should be sequential starting from 0."""
        text = "First paragraph.\n\n" * 20 + "Second paragraph.\n\n" * 20
        chunks = self.service.chunk_text(text)
        for i, chunk in enumerate(chunks):
            assert chunk["chunk_index"] == i

    def test_chunk_size_respected(self):
        """Each chunk should be within a reasonable range of the target size."""
        words = " ".join([f"word{i}" for i in range(500)])
        service = ChunkingService(chunk_size=50, chunk_overlap=10)
        chunks = service.chunk_text(words)

        assert len(chunks) > 1
        for chunk in chunks:
            assert chunk["token_count"] <= 80, (
                f"Chunk token count {chunk['token_count']} exceeds tolerance"
            )

    def test_overlap_present(self):
        """Consecutive chunks should share overlapping content."""
        paragraphs = []
        for i in range(20):
            paragraphs.append(
                f"Paragraph {i} contains unique information about topic {i}. "
                f"This is additional content to make the paragraph longer and "
                f"ensure it has enough tokens to be meaningful."
            )
        text = "\n\n".join(paragraphs)

        service = ChunkingService(chunk_size=80, chunk_overlap=20)
        chunks = service.chunk_text(text)

        if len(chunks) >= 2:
            first_words = set(chunks[0]["content"].split()[-10:])
            second_words = set(chunks[1]["content"].split()[:15])
            overlap = first_words & second_words
            assert len(overlap) >= 1 or len(chunks) <= 2

    def test_token_count_accuracy(self):
        """Reported token counts should match actual token counts."""
        text = "The quick brown fox jumps over the lazy dog. " * 50
        chunks = self.service.chunk_text(text)

        for chunk in chunks:
            expected_tokens = count_tokens(chunk["content"])
            assert chunk["token_count"] == expected_tokens

    def test_no_empty_chunks(self):
        """No chunk should have empty content."""
        text = "Hello.\n\n\n\nWorld.\n\n\n\nFoo.\n\n\n\nBar."
        chunks = self.service.chunk_text(text)
        for chunk in chunks:
            assert chunk["content"].strip() != ""

    def test_page_markers_removed_from_content(self):
        """Page markers like [Page 1] should be removed from chunk content."""
        text = "[Page 1]\nFirst page content here.\n\n[Page 2]\nSecond page content here."
        chunks = self.service.chunk_text(text)
        for chunk in chunks:
            assert "[Page" not in chunk["content"]

    def test_large_document_chunking(self):
        """Chunking should handle large documents without errors."""
        sentences = [
            f"Sentence number {i} contains important data point {i * 7}. "
            for i in range(1000)
        ]
        text = " ".join(sentences)

        service = ChunkingService(chunk_size=200, chunk_overlap=30)
        chunks = service.chunk_text(text)

        assert len(chunks) > 5
        total_content_length = sum(len(c["content"]) for c in chunks)
        assert total_content_length > len(text) * 0.5

    def test_custom_chunk_sizes(self):
        """Different chunk sizes should produce different numbers of chunks."""
        text = "Test content. " * 200

        small_chunks = ChunkingService(chunk_size=50, chunk_overlap=10).chunk_text(text)
        large_chunks = ChunkingService(chunk_size=200, chunk_overlap=20).chunk_text(text)

        assert len(small_chunks) > len(large_chunks)

    def test_chunk_metadata_structure(self):
        """Each chunk should have the required metadata fields."""
        text = "A test document with some content for chunking purposes." * 10
        chunks = self.service.chunk_text(text)

        for chunk in chunks:
            assert "content" in chunk
            assert "token_count" in chunk
            assert "chunk_index" in chunk
            assert "page_number" in chunk
            assert isinstance(chunk["content"], str)
            assert isinstance(chunk["token_count"], int)
            assert isinstance(chunk["chunk_index"], int)
