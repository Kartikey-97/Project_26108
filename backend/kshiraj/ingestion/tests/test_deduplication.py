"""
kshiraj/ingestion/tests/test_deduplication.py

Unit tests for DocumentDeduplicator and SHA-256 state evaluation.
"""

from __future__ import annotations

import pytest

from kshiraj.ingestion.deduplication import DocumentDeduplicator, DocumentState


class TestDocumentDeduplicator:

    def test_new_document_detection(self):
        dedup = DocumentDeduplicator()
        hash1 = dedup.calculate_hash(b"Content version 1")

        state = dedup.evaluate_document("https://bis.gov.in/doc1", hash1)
        assert state == DocumentState.NEW_DOCUMENT

    def test_unchanged_document_detection(self):
        dedup = DocumentDeduplicator()
        hash1 = dedup.calculate_hash(b"Content version 1")

        # First evaluation: new
        dedup.evaluate_document("https://bis.gov.in/doc1", hash1)

        # Second evaluation with same URL and hash: unchanged
        state2 = dedup.evaluate_document("https://bis.gov.in/doc1", hash1)
        assert state2 == DocumentState.UNCHANGED_DOCUMENT

    def test_modified_document_detection(self):
        dedup = DocumentDeduplicator()
        hash1 = dedup.calculate_hash(b"Content version 1")
        hash2 = dedup.calculate_hash(b"Content version 2 (Amended)")

        dedup.evaluate_document("https://bis.gov.in/doc1", hash1)
        state_mod = dedup.evaluate_document("https://bis.gov.in/doc1", hash2)

        assert state_mod == DocumentState.MODIFIED_DOCUMENT
        assert dedup.get_hash_for_url("https://bis.gov.in/doc1") == hash2

    def test_duplicate_across_urls(self):
        dedup = DocumentDeduplicator()
        hash1 = dedup.calculate_hash(b"Shared Gazette PDF")

        dedup.evaluate_document("https://egazette.gov.in/notif1.pdf", hash1)
        state_dup = dedup.evaluate_document("https://dpiit.gov.in/mirrored_notif1.pdf", hash1)

        assert state_dup == DocumentState.DUPLICATE_URL
