"""
Text Splitter — AI-Powered Study Buddy
========================================
Splits raw text into overlapping chunks suitable for embedding.
Uses LangChain's RecursiveCharacterTextSplitter for smart splitting
that respects sentence and paragraph boundaries.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.config import settings

logger = logging.getLogger("study_buddy.splitter")


@dataclass
class TextChunk:
    """A single text chunk with its metadata."""
    content:    str
    chunk_index: int
    char_start: int
    char_end:   int
    source:     str = ""


def split_text(
    text: str,
    source: str = "",
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[TextChunk]:
    """
    Split *text* into overlapping chunks.

    Args:
        text:          Raw extracted text.
        source:        Source label (filename) stored in metadata.
        chunk_size:    Token size per chunk (defaults to settings.CHUNK_SIZE).
        chunk_overlap: Overlap between chunks (defaults to settings.CHUNK_OVERLAP).

    Returns:
        List of TextChunk objects.
    """
    size    = chunk_size    or settings.CHUNK_SIZE
    overlap = chunk_overlap or settings.CHUNK_OVERLAP

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

    raw_chunks = splitter.split_text(text)

    # Filter out tiny chunks
    chunks: list[TextChunk] = []
    pos = 0
    for idx, chunk in enumerate(raw_chunks):
        if len(chunk.strip()) < 50:  # skip near-empty chunks
            continue
        start = text.find(chunk, pos)
        end   = start + len(chunk) if start != -1 else pos + len(chunk)
        chunks.append(TextChunk(
            content=chunk.strip(),
            chunk_index=idx,
            char_start=max(start, 0),
            char_end=end,
            source=source,
        ))
        pos = max(start, 0)

    logger.info(
        "Split '%s' into %d chunks (size=%d, overlap=%d)",
        source, len(chunks), size, overlap,
    )
    return chunks
