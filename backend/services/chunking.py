"""
NexusAI — Chunking Service
Recursive text splitting with overlap and token counting.
"""

import logging
import re
from typing import Dict, List, Optional

from utils.helpers import count_tokens

logger = logging.getLogger("nexusai.chunking")


class ChunkingService:
    """Splits documents into overlapping chunks optimized for embedding and retrieval."""

    SEPARATORS = ["\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " "]

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        """Initialize the chunking service.

        Args:
            chunk_size: Target token count per chunk.
            chunk_overlap: Number of overlapping tokens between consecutive chunks.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(self, text: str) -> List[Dict]:
        """Split text into overlapping chunks with metadata.

        Args:
            text: The full document text to chunk.

        Returns:
            List of dicts with keys: content, token_count, chunk_index, page_number.
        """
        if not text or not text.strip():
            return []

        page_map = self._build_page_map(text)
        clean_text = re.sub(r"\[Page \d+\]\n", "", text)

        raw_chunks = self._recursive_split(clean_text, self.SEPARATORS)

        merged_chunks = self._merge_chunks(raw_chunks)

        results = []
        for idx, chunk_content in enumerate(merged_chunks):
            token_count = count_tokens(chunk_content)
            page_number = self._find_page_number(chunk_content, page_map)
            results.append({
                "content": chunk_content,
                "token_count": token_count,
                "chunk_index": idx,
                "page_number": page_number,
            })

        logger.info(f"📦 Created {len(results)} chunks (target: {self.chunk_size} tokens, overlap: {self.chunk_overlap})")
        return results

    def _recursive_split(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using a hierarchy of separators.

        Tries each separator in order. If a segment is still too large,
        recursively splits with the next separator in the list.
        """
        if not separators:
            return [text] if text.strip() else []

        separator = separators[0]
        remaining_separators = separators[1:]

        parts = text.split(separator)

        results = []
        for part in parts:
            part = part.strip()
            if not part:
                continue

            token_count = count_tokens(part)
            if token_count <= self.chunk_size:
                results.append(part)
            elif remaining_separators:
                sub_parts = self._recursive_split(part, remaining_separators)
                results.extend(sub_parts)
            else:
                words = part.split(" ")
                current_segment = []
                current_tokens = 0
                for word in words:
                    word_tokens = count_tokens(word)
                    if current_tokens + word_tokens > self.chunk_size and current_segment:
                        results.append(" ".join(current_segment))
                        current_segment = []
                        current_tokens = 0
                    current_segment.append(word)
                    current_tokens += word_tokens
                if current_segment:
                    results.append(" ".join(current_segment))

        return results

    def _merge_chunks(self, chunks: List[str]) -> List[str]:
        """Merge small chunks and add overlap between consecutive chunks.

        Combines chunks that are smaller than the target size, then adds
        overlap by prepending the tail of the previous chunk.
        """
        if not chunks:
            return []

        merged = []
        current = chunks[0]
        current_tokens = count_tokens(current)

        for i in range(1, len(chunks)):
            next_chunk = chunks[i]
            next_tokens = count_tokens(next_chunk)

            if current_tokens + next_tokens <= self.chunk_size:
                current = current + "\n\n" + next_chunk
                current_tokens = count_tokens(current)
            else:
                merged.append(current)
                if self.chunk_overlap > 0:
                    overlap_text = self._get_overlap_text(current, self.chunk_overlap)
                    current = overlap_text + "\n\n" + next_chunk if overlap_text else next_chunk
                else:
                    current = next_chunk
                current_tokens = count_tokens(current)

        if current.strip():
            merged.append(current)

        return merged

    def _get_overlap_text(self, text: str, overlap_tokens: int) -> str:
        """Extract the last N tokens of text for overlap."""
        words = text.split()
        overlap_words = []
        token_count = 0

        for word in reversed(words):
            word_count = count_tokens(word)
            if token_count + word_count > overlap_tokens:
                break
            overlap_words.insert(0, word)
            token_count += word_count

        return " ".join(overlap_words)

    def _build_page_map(self, text: str) -> Dict[str, int]:
        """Build a mapping from text segments to page numbers."""
        page_map = {}
        page_pattern = re.compile(r"\[Page (\d+)\]\n(.*?)(?=\[Page \d+\]|\Z)", re.DOTALL)

        for match in page_pattern.finditer(text):
            page_num = int(match.group(1))
            content = match.group(2).strip()
            if content:
                first_sentence = content[:200]
                page_map[first_sentence] = page_num

        return page_map

    def _find_page_number(self, chunk: str, page_map: Dict[str, int]) -> Optional[int]:
        """Find the page number for a chunk using the page map."""
        chunk_start = chunk[:200]
        for text_key, page_num in page_map.items():
            if text_key in chunk_start or chunk_start in text_key:
                return page_num
        return None
