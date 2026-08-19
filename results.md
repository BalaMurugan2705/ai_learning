# Week 4 RAG Evaluation

## 1. Corpus

The evaluation corpus contains six SDK reference documents:

- client.md
- authentication.md
- requests.md
- responses.md
- pagination.md
- errors.md

An additional `client_v2.md` document is used specifically for the metadata filtering experiment.

---

## 2. Embedding Model

Embedding model:

`all-MiniLM-L6-v2`

Embedding dimension:

`384`

---

## 3. Vector Database

Vector database:

`Chroma`

Two collections were evaluated:

- `sdk_docs_simple`
- `sdk_docs_structure`

---

## 4. Retrieval Evaluation

Eight known-answer questions were evaluated using Top-K = 5.

### Simple Chunker

Hit@5:

`8/8`

### Structure-Aware Chunker

Hit@5:

`8/8`

The initial source-file-based metric did not distinguish the two strategies, so the evaluation was tightened to inspect whether the retrieved chunk contained the expected answer.

---

## 5. Metadata Filtering

The corpus contains two versions of the Client documentation:

| Version | retry_backoff_ms |
|---|---:|
| v2 | 1000 |
| v3 | 500 |

Without a version filter, retrieval can return both versions.

With:

`sdk_version = v3`

the search is restricted to v3 documentation and the correct v3 value is retrieved.

---

## 6. Retrieval Distance Calibration

Known answerable questions produced distances:

- Q1: 0.480
- Q2: 0.577
- Q3: 0.637

Known unanswerable questions produced:

- Q4: 1.041
- Q5: 1.178
- Q6: 1.003

Based on this controlled evaluation corpus, a retrieval distance threshold of `0.8` was selected.

This threshold is specific to this experiment and is not treated as a universal value.

---

## 7. Grounded Generation

The generation model is Groq.

The model receives only the retrieved documentation as context.

The prompt instructs the model:

- answer only from the provided documentation
- do not use outside knowledge
- do not guess
- refuse when the documentation is insufficient

---

## 8. Refusal Test

Questions that are not answered by the corpus should produce:

`I don't know based on the provided documents.`

No unsupported source or fabricated detail should be returned.

---

## 9. Citations

Sources are generated from retrieved Chroma metadata rather than invented by the LLM.

Each source contains:

- source file
- page ID
- section

## 10. Retrieval Failure / Diagnosis

### Failure

Question:

"What is the default value of retry_backoff_ms?"

Unfiltered retrieval returned evidence from both:

- client_v2.md → 1000
- client.md → 500

### Diagnosis

The retriever correctly found semantically relevant documents, but the query did not specify the SDK version.

The problem was therefore not primarily semantic retrieval failure. It was a metadata/version ambiguity problem.

### Fix

Apply:

`sdk_version = v3`

during retrieval when the user asks about the v3 SDK.

This restricts the candidate documents before similarity ranking and prevents the v2 value from being used.