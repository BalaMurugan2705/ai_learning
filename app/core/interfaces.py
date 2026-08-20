"""Abstractions the services layer depends on. Concrete adapters live in
app/infrastructure/ and are wired in by app/core/dependencies.py — nothing
in app/services ever imports chromadb, sentence_transformers, or groq
directly, so swapping any of them (a different vector DB, a different LLM
provider) never requires touching business logic, only the adapter and the
composition root.

Protocol, not ABC: structural typing means an adapter satisfies an
interface by having the right shape, with no inheritance coupling required.
"""
from typing import Optional, Protocol, runtime_checkable

from app.core.models import RetrievedChunk


@runtime_checkable
class EmbeddingProvider(Protocol):
    def embed(self, text: str) -> list[float]: ...


@runtime_checkable
class VectorStore(Protocol):
    def upsert(self, chunks: list[dict], embeddings: list[list[float]]) -> None: ...

    def query(
        self,
        query_embedding: list[float],
        top_k: int,
        where: Optional[dict] = None,
    ) -> list[RetrievedChunk]: ...


@runtime_checkable
class AnswerGenerator(Protocol):
    def generate(self, question: str, context: str) -> str: ...


@runtime_checkable
class ChunkingStrategy(Protocol):
    def chunk(
        self,
        text: str,
        *,
        source_file: str,
        page_id: str,
        sdk_version: str,
        page_type: str,
    ) -> list[dict]: ...


@runtime_checkable
class TextExtractor(Protocol):
    """One supported upload format. `ExtensionBasedTextExtractor` dispatches
    to whichever registered extractor supports() a given extension — adding
    a format means adding an extractor, not editing existing ones."""

    def supports(self, extension: str) -> bool: ...

    def extract(self, content: bytes) -> str: ...
