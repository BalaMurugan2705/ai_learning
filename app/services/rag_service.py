"""The RAG pipeline: embed the question, retrieve candidate chunks, decide
whether they're relevant enough to answer from, and if so generate a
grounded answer with citations back to real chunk_ids.

RagService depends only on EmbeddingProvider, VectorStore, and
AnswerGenerator — never on sentence-transformers, chromadb, or Groq
directly, so any of the three can be swapped without touching this class.
"""
from typing import Optional

from app.core.interfaces import AnswerGenerator, EmbeddingProvider, VectorStore
from app.core.models import AnswerResult, RetrievedChunk


class RagService:
    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
        answer_generator: AnswerGenerator,
        top_k: int,
        refusal_distance_threshold: float,
        refusal_message: str,
    ):
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._answer_generator = answer_generator
        self._top_k = top_k
        self._refusal_distance_threshold = refusal_distance_threshold
        self._refusal_message = refusal_message

    def answer(self, question: str, sdk_version: Optional[str] = None) -> AnswerResult:
        chunks = self._retrieve(question, sdk_version=sdk_version)

        # The refusal is forced by this distance threshold, before the LLM
        # is ever called — not left to the model's own judgment.
        if not self._is_relevant_enough(chunks):
            return AnswerResult(self._refusal_message, [])

        context = self._build_context(chunks)
        answer = self._answer_generator.generate(question=question, context=context)
        sources = self._build_sources(chunks)

        return AnswerResult(answer, sources)

    def _retrieve(self, question: str, sdk_version: Optional[str]) -> list[RetrievedChunk]:
        query_vector = self._embedding_provider.embed(question)
        where = {"sdk_version": sdk_version} if sdk_version else None

        chunks = self._vector_store.query(query_vector, top_k=self._top_k, where=where)

        best_distance = chunks[0].distance if chunks else float("inf")
        # Deliberately a print, not a log line: this exact "Best retrieval
        # distance: <n>" text is the refusal evidence pasted into
        # results.md's transcripts and reproduced by
        # app/scripts/test_grounding.py.
        print("\nBest retrieval distance:", best_distance)

        return chunks

    def _is_relevant_enough(self, chunks: list[RetrievedChunk]) -> bool:
        return bool(chunks) and chunks[0].distance <= self._refusal_distance_threshold

    @staticmethod
    def _build_context(chunks: list[RetrievedChunk]) -> str:
        parts = [
            f"SOURCE FILE: {chunk.metadata['source_file']}\n"
            f"PAGE: {chunk.metadata['page_id']}\n"
            f"SECTION: {chunk.metadata.get('section', '')}\n\n"
            f"{chunk.text}"
            for chunk in chunks
        ]

        return "\n\n".join(parts)

    @staticmethod
    def _build_sources(chunks: list[RetrievedChunk]) -> list[dict]:
        """Citations come straight from the vector store's own ids/metadata
        — never invented by the LLM — so every citation resolves to a real
        chunk."""
        sources = []

        for chunk in chunks:
            source = {
                "chunk_id": chunk.chunk_id,
                "source_file": chunk.metadata["source_file"],
                "page_id": chunk.metadata["page_id"],
                "section": chunk.metadata.get("section", ""),
            }

            if source not in sources:
                sources.append(source)

        return sources
