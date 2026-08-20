# Docs Assistant

A retrieval-augmented Q&A service over versioned SDK reference documentation. Upload
docs, ask questions in a chat UI, get answers grounded in real chunks with citations —
or a forced refusal when the corpus doesn't contain the answer.

## Architecture

Ports and adapters: `services/` (business logic) depends only on the interfaces in
`core/interfaces.py`, never on a concrete vector DB, embedding model, or LLM SDK.
Concrete adapters live in `infrastructure/`. `core/dependencies.py` is the one place
that wires an adapter to an interface and hands the result to a service — the
composition root. Swapping Chroma for another vector DB, or Groq for another LLM,
means writing one new adapter class and changing one line in `dependencies.py`;
nothing in `services/` or `api/` changes.

```
app/
  main.py                    FastAPI app: startup, routing, health check, error handling
  api/
    routes.py                 HTTP endpoints — receive services via Depends(...), never
                               import or construct a concrete implementation themselves
    schemas.py                 Request/response models
  core/
    interfaces.py               The abstractions: EmbeddingProvider, VectorStore,
                                 AnswerGenerator, ChunkingStrategy, TextExtractor
    models.py                    Shared data types: RetrievedChunk, AnswerResult
    dependencies.py              Composition root — the only module that imports
                                  both an interface and its concrete adapter
    config.py                    Settings (env-driven, validated at startup) + corpus manifest
    logging_config.py            Logging setup
    document_loader.py           Reads a document from a path on disk (single
                                  implementation — not a variation point, no interface)
  infrastructure/               Concrete adapters — the only place that imports
                                 chromadb / sentence_transformers / groq / pypdf
    vector_store.py               ChromaVectorStore implements VectorStore
    embeddings.py                 SentenceTransformerEmbeddingProvider implements EmbeddingProvider
    generator.py                  GroqAnswerGenerator implements AnswerGenerator
    document_extractors.py        PlainTextExtractor / PdfTextExtractor implement TextExtractor
  services/
    chunking.py                  SimpleChunker / StructureAwareChunker implement ChunkingStrategy
    ingestion_service.py          IngestionService: chunk -> embed -> upsert
    rag_service.py                 RagService: retrieve -> refuse-if-irrelevant -> generate -> cite
  scripts/                      Standalone CLI tools (see below) — run with `python -m`
  static/, templates/            Frontend (vanilla JS chat UI)
```

Design choices worth knowing about:

- **Services depend on interfaces, not concretions.** `RagService` and
  `IngestionService` take an `EmbeddingProvider` / `VectorStore` / `AnswerGenerator` /
  `ChunkingStrategy` in their constructor and only ever call methods on those
  interfaces. They have no import of chromadb, sentence-transformers, or groq.
- **Refusal is forced, not suggested.** `RagService.answer` checks the top retrieval
  distance against `refusal_distance_threshold` *before* calling the LLM. If nothing
  relevant enough was retrieved, the app refuses deterministically instead of asking
  the model to judge its own context.
- **Citations come from the vector store, not the LLM.** Every source in an answer is
  a `chunk_id` returned by the vector store's own query result — never invented by the
  model.
- **Config fails fast.** `Settings` is a `pydantic-settings` model; a missing
  `GROQ_API_KEY` raises a clear validation error at startup instead of a confusing
  401 on the first question asked.
- **Adapters are lazy singletons, injected, not imported.** `core/dependencies.py`
  builds each adapter behind `functools.lru_cache` and exposes it as a FastAPI
  dependency (`Depends(get_rag_service)`) — routes and scripts ask for a capability,
  they don't reach into another module and call a concrete instance directly.

## Setup

Requires Python 3.11+.

```bash
python -m venv .venv
.venv/Scripts/activate        # .venv/bin/activate on macOS/Linux
pip install -r requirements.txt
cp app/.env.example app/.env  # then fill in GROQ_API_KEY
```

## Run

```bash
uvicorn app.main:app --reload --port 5000
```

Open http://localhost:5000. Health check: `GET /health`.

## Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/` | GET | Chat UI |
| `/upload` | POST | Upload a `.md`/`.txt`/`.pdf` file, chunk + embed + index it |
| `/ask` | POST | `{"question": "...", "sdk_version": "v3"}` -> `{"answer", "sources"}` |
| `/health` | GET | Liveness check |

## Scripts

The initial corpus (`data/docs/`) and evaluation tooling live under `app/scripts/`,
run as modules from the repo root:

```bash
python -m app.scripts.ingest_simple        # index the corpus with the fixed-width chunker
python -m app.scripts.ingest_structure     # index the corpus with the structure-aware chunker
python -m app.scripts.evaluate_retrieval   # hit@5 for both chunkers over the known-answer set
python -m app.scripts.filter_test          # unfiltered vs. sdk_version-filtered retrieval demo
python -m app.scripts.test_grounding       # answerable + refused questions through the full pipeline
python -m app.scripts.chat                 # interactive one-question REPL
```

On Windows, section names contain `→`; set `PYTHONIOENCODING=utf-8` first if the
console raises a `UnicodeEncodeError`.

## Evaluation

[`results.md`](results.md) documents the graded retrieval evaluation (chunking
strategy comparison, metadata filtering, citation/refusal behavior) written for the
coursework in [`TASK/`](TASK/). It reflects the module paths and pipeline behavior in
this codebase.
