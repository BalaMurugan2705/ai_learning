"""The composition root: the one place concrete adapters get constructed
and wired into the services that depend on their interfaces. Every function
here is also a FastAPI dependency provider — routes ask for a service via
`Depends(get_rag_service)` instead of importing and calling a concrete
singleton directly.

`lru_cache` gives each provider process-lifetime singleton behavior (the
embedding model, Chroma client, and Groq client are all expensive to
construct and safe to share) without a separate DI container library.
"""
from functools import lru_cache

from app.core.config import settings
from app.infrastructure.document_extractors import (
    ExtensionBasedTextExtractor,
    PdfTextExtractor,
    PlainTextExtractor,
)
from app.infrastructure.embeddings import SentenceTransformerEmbeddingProvider
from app.infrastructure.generator import GroqAnswerGenerator
from app.infrastructure.vector_store import ChromaVectorStore, build_chroma_client
from app.services.chunking import StructureAwareChunker
from app.services.ingestion_service import IngestionService
from app.services.rag_service import RagService


@lru_cache(maxsize=1)
def get_embedding_provider() -> SentenceTransformerEmbeddingProvider:
    return SentenceTransformerEmbeddingProvider(settings.embedding_model_name)


@lru_cache(maxsize=1)
def get_chroma_client():
    return build_chroma_client(settings.chroma_db_path)


@lru_cache(maxsize=1)
def get_simple_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(get_chroma_client(), settings.simple_collection_name)


@lru_cache(maxsize=1)
def get_structure_vector_store() -> ChromaVectorStore:
    return ChromaVectorStore(get_chroma_client(), settings.structure_collection_name)


@lru_cache(maxsize=1)
def get_answer_generator() -> GroqAnswerGenerator:
    return GroqAnswerGenerator(
        api_key=settings.groq_api_key.get_secret_value(),
        model=settings.groq_model,
        temperature=settings.generation_temperature,
        refusal_message=settings.refusal_message,
    )


@lru_cache(maxsize=1)
def get_text_extractor() -> ExtensionBasedTextExtractor:
    return ExtensionBasedTextExtractor([PlainTextExtractor(), PdfTextExtractor()])


@lru_cache(maxsize=1)
def get_ingestion_service() -> IngestionService:
    return IngestionService(
        chunking_strategy=StructureAwareChunker(settings.structure_chunk_overlap_chars),
        embedding_provider=get_embedding_provider(),
        vector_store=get_structure_vector_store(),
    )


@lru_cache(maxsize=1)
def get_rag_service() -> RagService:
    return RagService(
        embedding_provider=get_embedding_provider(),
        vector_store=get_structure_vector_store(),
        answer_generator=get_answer_generator(),
        top_k=settings.retrieval_top_k,
        refusal_distance_threshold=settings.refusal_distance_threshold,
        refusal_message=settings.refusal_message,
    )
