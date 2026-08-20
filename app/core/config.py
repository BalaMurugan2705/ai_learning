"""Central configuration for the app.

Every tunable value the RAG pipeline depends on — model names, chunking
parameters, retrieval/refusal thresholds, collection names, ingestion
defaults, the corpus manifest — lives here instead of being hardcoded
across modules. Change a value once, here, and every value is also
overridable via an environment variable or app/.env, and missing/invalid
config fails fast at startup instead of surfacing as a confusing error
the first time a dependent module is used.
"""
from functools import lru_cache
from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

APP_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=APP_DIR / ".env",
        env_file_encoding="utf-8",
        frozen=True,
        extra="ignore",
    )

    # --- Groq / generation ---
    # SecretStr so the key never gets printed in a traceback, log line, or
    # a stray `print(settings)`. Required — no default — so a missing
    # GROQ_API_KEY fails immediately at startup with a clear error instead
    # of an opaque 401 the first time a question is asked.
    groq_api_key: SecretStr
    groq_model: str = "openai/gpt-oss-120b"
    generation_temperature: float = 0
    refusal_message: str = "I don't know based on the provided documents."

    # --- Embeddings ---
    embedding_model_name: str = "all-MiniLM-L6-v2"

    # --- Vector store ---
    chroma_db_path: str = "./chroma_db"
    simple_collection_name: str = "sdk_docs_simple"
    structure_collection_name: str = "sdk_docs_structure"

    # --- Chunking ---
    simple_chunk_size: int = 300
    simple_chunk_overlap: int = 50
    # Structure-aware chunks are already whole, header-bounded sections, not
    # mid-sentence cuts — overlap has no boundary-cut problem to fix there,
    # and was measured to actively hurt retrieval on this corpus (diluted a
    # tight parameter-table chunk enough to push a previously-answerable
    # query over the refusal threshold). Left at 0 by default; still
    # available for a corpus with longer sections.
    structure_chunk_overlap_chars: int = 0

    # --- Retrieval / refusal ---
    retrieval_top_k: int = 5
    refusal_distance_threshold: float = 0.8

    # --- Ingestion defaults ---
    default_sdk_version: str = "v3"
    default_page_type: str = "reference"

    # --- Upload ---
    allowed_upload_extensions: frozenset[str] = frozenset({".md", ".txt", ".pdf"})


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


# Corpus manifest for the standalone ingest scripts (app/scripts/ingest_*.py).
# Not a "setting" in the tunable-parameter sense above — this is sample data
# describing which files exist and how they're tagged — but it lives here too
# so app/core/config.py stays the one place to look for anything configurable.
DOCUMENTS = [
    {
        "file": "client.md",
        "page_id": "client",
        "sdk_version": "v3",
        "page_type": "reference",
    },
    {
        "file": "authentication.md",
        "page_id": "authentication",
        "sdk_version": "v3",
        "page_type": "reference",
    },
    {
        "file": "requests.md",
        "page_id": "requests",
        "sdk_version": "v3",
        "page_type": "reference",
    },
    {
        "file": "responses.md",
        "page_id": "responses",
        "sdk_version": "v3",
        "page_type": "reference",
    },
    {
        "file": "pagination.md",
        "page_id": "pagination",
        "sdk_version": "v3",
        "page_type": "reference",
    },
    {
        "file": "errors.md",
        "page_id": "errors",
        "sdk_version": "v3",
        "page_type": "reference",
    },
    {
        "file": "client_v2.md",
        "page_id": "client",
        "sdk_version": "v2",
        "page_type": "reference",
    },
]
