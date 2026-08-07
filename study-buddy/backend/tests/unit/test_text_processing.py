"""
Unit Tests — Text Extractor & Splitter
========================================
Tests for text extraction helpers and chunking logic.
No external dependencies — uses in-memory data.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from app.utils.text_splitter import split_text, TextChunk


# ---------------------------------------------------------------------------
# Text Splitter tests
# ---------------------------------------------------------------------------

class TestTextSplitter:
    SAMPLE = """
    Introduction to Machine Learning

    Machine learning is a subset of artificial intelligence that enables computers
    to learn from data without being explicitly programmed. It uses algorithms that
    improve automatically through experience.

    There are three main types of machine learning:

    1. Supervised Learning: The algorithm learns from labelled training data.
       Examples include linear regression, decision trees, and neural networks.

    2. Unsupervised Learning: The algorithm finds hidden patterns in unlabelled data.
       Examples include k-means clustering and principal component analysis.

    3. Reinforcement Learning: The algorithm learns by interacting with an environment
       and receiving rewards or penalties based on its actions.

    Applications of machine learning include image recognition, natural language
    processing, recommendation systems, and autonomous vehicles.
    """ * 3  # Repeat to ensure multiple chunks

    def test_returns_list_of_chunks(self):
        chunks = split_text(self.SAMPLE, source="test.txt")
        assert isinstance(chunks, list)
        assert len(chunks) > 0

    def test_chunks_are_text_chunk_objects(self):
        chunks = split_text(self.SAMPLE, source="test.txt")
        for chunk in chunks:
            assert isinstance(chunk, TextChunk)

    def test_chunk_content_not_empty(self):
        chunks = split_text(self.SAMPLE, source="test.txt")
        for chunk in chunks:
            assert len(chunk.content.strip()) >= 50

    def test_source_label_stored(self):
        chunks = split_text(self.SAMPLE, source="biology.pdf")
        for chunk in chunks:
            assert chunk.source == "biology.pdf"

    def test_custom_chunk_size(self):
        chunks_small = split_text(self.SAMPLE, chunk_size=200, chunk_overlap=20)
        chunks_large = split_text(self.SAMPLE, chunk_size=800, chunk_overlap=50)
        assert len(chunks_small) >= len(chunks_large)

    def test_empty_text_returns_empty_list(self):
        chunks = split_text("", source="empty.txt")
        assert chunks == []

    def test_tiny_text_below_threshold_filtered(self):
        chunks = split_text("Hi.", source="tiny.txt")
        assert chunks == []


# ---------------------------------------------------------------------------
# File Validator tests
# ---------------------------------------------------------------------------

class TestFileValidator:
    def test_valid_txt_file(self):
        from app.utils.file_validator import validate_upload
        result = validate_upload(b"Hello, world!", "notes.txt")
        assert result == "txt"

    def test_valid_pdf_magic_bytes(self):
        from app.utils.file_validator import validate_upload
        pdf_bytes = b"%PDF-1.4 fake content"
        result = validate_upload(pdf_bytes, "document.pdf")
        assert result == "pdf"

    def test_invalid_extension_raises(self):
        from app.utils.file_validator import validate_upload
        from app.exceptions import UnsupportedFileTypeError
        with pytest.raises(UnsupportedFileTypeError):
            validate_upload(b"content", "malware.exe")

    def test_file_too_large_raises(self):
        from app.utils.file_validator import validate_upload
        from app.exceptions import FileTooLargeError
        # Simulate a 51 MB file
        big_content = b"x" * (51 * 1024 * 1024)
        with pytest.raises(FileTooLargeError):
            validate_upload(big_content, "big.txt")

    def test_pdf_wrong_magic_raises(self):
        from app.utils.file_validator import validate_upload
        from app.exceptions import UnsupportedFileTypeError
        with pytest.raises(UnsupportedFileTypeError):
            validate_upload(b"NOT_A_PDF_CONTENT", "fake.pdf")
