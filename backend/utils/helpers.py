"""
NexusAI — Utility Helpers
Token counting, text cleaning, and general utilities.
"""

import re
from typing import Optional

import tiktoken


_encoder: Optional[tiktoken.Encoding] = None


def _get_encoder() -> tiktoken.Encoding:
    """Lazy-load the tiktoken encoder for cl100k_base (used for token counting)."""
    global _encoder
    if _encoder is None:
        _encoder = tiktoken.get_encoding("cl100k_base")
    return _encoder


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text string.

    Args:
        text: Input text.

    Returns:
        Number of tokens.
    """
    if not text:
        return 0
    encoder = _get_encoder()
    return len(encoder.encode(text))


def truncate_text(text: str, max_tokens: int) -> str:
    """Truncate text to a maximum number of tokens.

    Args:
        text: Input text.
        max_tokens: Maximum number of tokens.

    Returns:
        Truncated text.
    """
    if not text:
        return ""
    encoder = _get_encoder()
    tokens = encoder.encode(text)
    if len(tokens) <= max_tokens:
        return text
    truncated_tokens = tokens[:max_tokens]
    return encoder.decode(truncated_tokens)


def clean_text(text: str) -> str:
    """Clean and normalize text content.

    - Remove excessive whitespace
    - Normalize unicode characters
    - Strip control characters
    """
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\x20-\x7E\n\r\t]", "", text)
    text = text.strip()
    return text


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to a human-readable string.

    Args:
        size_bytes: File size in bytes.

    Returns:
        Formatted string like '2.4 MB'.
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing potentially dangerous characters.

    Args:
        filename: Original filename.

    Returns:
        Sanitized filename safe for filesystem use.
    """
    sanitized = re.sub(r'[<>:"/\\|?*]', "_", filename)
    sanitized = re.sub(r"\.{2,}", ".", sanitized)
    sanitized = sanitized.strip(". ")
    if not sanitized:
        sanitized = "unnamed_file"
    return sanitized


def generate_chunk_id(document_id: str, chunk_index: int) -> str:
    """Generate a deterministic chunk ID.

    Args:
        document_id: Parent document ID.
        chunk_index: Index of the chunk within the document.

    Returns:
        Formatted chunk ID string.
    """
    return f"{document_id}_{chunk_index}"
