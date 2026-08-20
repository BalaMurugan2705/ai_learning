from app.core.interfaces import ChunkingStrategy, EmbeddingProvider, VectorStore


class IngestionService:
    """Chunk -> embed -> upsert. Depends only on the ChunkingStrategy,
    EmbeddingProvider, and VectorStore interfaces — never on chromadb,
    sentence-transformers, or a specific chunking algorithm directly, so any
    of the three can be swapped independently."""

    def __init__(
        self,
        chunking_strategy: ChunkingStrategy,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStore,
    ):
        self._chunking_strategy = chunking_strategy
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store

    def ingest(self, filename: str, text: str, sdk_version: str, page_type: str) -> int:
        page_id = filename.rsplit(".", 1)[0]

        chunks = self._chunking_strategy.chunk(
            text,
            source_file=filename,
            page_id=page_id,
            sdk_version=sdk_version,
            page_type=page_type,
        )

        embeddings = [self._embedding_provider.embed(chunk["text"]) for chunk in chunks]

        self._vector_store.upsert(chunks, embeddings)

        return len(chunks)
