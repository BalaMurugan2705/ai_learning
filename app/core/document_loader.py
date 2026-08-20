"""Reads document text from a path on disk, for the ingest scripts against
the local corpus. Upload-time extraction (from raw bytes, per format) is a
genuine variation point and lives behind TextExtractor in
app/infrastructure/document_extractors.py instead."""
from pathlib import Path


def load_document(file_path) -> str:
    return Path(file_path).read_text(encoding="utf-8")
