# Week 3/4 Practical — Task Set E — Results

## 0. Scope

Per requirement 6, the whole docs site was **not** re-indexed. Only the 6 supplied
v3 reference pages (`client.md`, `authentication.md`, `requests.md`, `responses.md`,
`pagination.md`, `errors.md`) were indexed, plus one additional `client_v2.md` page
used specifically to demonstrate the `sdk_version` metadata-filter bug in §4
(unfiltered retrieval currently prefers the v2 value of `retry_backoff_ms` over v3).

Embedding model: `all-MiniLM-L6-v2` (384-dim). Vector DB: Chroma, two collections:
`sdk_docs_simple` and `sdk_docs_structure`.

**Note on corpus hygiene:** while re-running this evaluation, the `sdk_docs_structure`
collection was found to contain 4 stale chunks (`client_v2-v3-0..3`) left over from an
earlier manual upload through the `/upload` endpoint — that endpoint doesn't derive
`sdk_version` from the filename, so it had tagged v2 client content as `sdk_version: v3`.
This silently corrupted the v3 corpus with a mislabeled v2 chunk. These were deleted
before the measurements below were taken.

**Note on project layout:** the app was reorganized into a layered package
(`app/core`, `app/services`, `app/api`, `app/scripts`) — see §10. All commands below
use the current module paths (e.g. `python -m app.scripts.evaluate_retrieval`).

---

## 1. Eight known-answer questions

Written from the pages first, before running any retrieval.

| ID | Question | Answer | Source page | Section |
|---|---|---|---|---|
| Q1 | What is the default value of retry_backoff_ms? | 500 | client.md | Client.send() → Parameters |
| Q2 | What type is the retry_backoff_ms parameter? | int | client.md | Client.send() → Parameters |
| Q3 | What is the default value of max_retries? | 3 | client.md | Client.send() → Parameters |
| Q4 | What value is passed to retry_backoff_ms in the Client.send() example? | 500 | client.md | Client.send() → Example |
| Q5 | Is api_key required for Authentication.configure()? | yes | authentication.md | Authentication.configure() → Parameters |
| Q6 | What is the default value of compression in Request.create()? | true | requests.md | Request.create() → Parameters |
| Q7 | What is the default page_size for Pagination.configure()? | 50 | pagination.md | Pagination.configure() → Parameters |
| Q8 | What does the strict parameter control in Response.parse()? | controls whether malformed response data causes an error | responses.md | Response.parse() → Parameters |

Q1–Q4 depend on a parameter-table row or a code-fence value (4 of 8, exceeds the
"at least 3" requirement).

---

## 2. Hit@5 — two chunking strategies, same 8 questions

**The first metric we tried was wrong.** Checking only "does the expected
`source_file` appear in the top 5" scores 8/8 for both strategies regardless of
chunk quality — with only 6-7 documents in the corpus, almost any query returns
the right file. That number measures corpus size, not chunking quality, so it was
discarded.

**Tightened metric:** a hit requires the top-5 chunk that actually contains the
expected answer text to come from the expected source file. Re-run against the
cleaned collections:

| ID | Simple chunker — hit? (rank) | Structure-aware chunker — hit? (rank) |
|---|---|---|
| Q1 | ✅ rank 1 | ✅ rank 2 |
| Q2 | ✅ rank 1 | ✅ rank 2 |
| Q3 | ✅ rank 1 | ✅ rank 2 |
| Q4 | ✅ rank 2 | ✅ rank 2 |
| Q5 | ✅ rank 1 | ✅ rank 2 |
| Q6 | ✅ rank 1 | ✅ rank 1 |
| Q7 | ✅ rank 1 | ✅ rank 1 |
| Q8 | ✅ rank 2 | ✅ rank 3 |
| **Hit@5** | **8/8** | **8/8** |

Both strategies still tie at 8/8 on this corpus even under the tightened metric — the
corpus is simply too small for either chunker to miss in the top 5.

**The number that actually moved: rank of the correct chunk.** (Simple chunker now
runs with a 50-character sliding-window overlap, §10 — Q5 moved from rank 2 to rank 1
as a result.)

| | Simple (20 chunks, overlap=50) | Structure-aware (40 chunks, overlap=0) |
|---|---|---|
| Rank-1 hits | 6/8 | 2/8 |
| Average rank of correct hit | 1.25 | 1.875 |

The structure-aware chunker produces 40 chunks vs. the simple chunker's 20 (it
splits on every markdown header, including nested `###` subsections). More,
finer-grained chunks means more near-duplicate competing chunks — e.g. an
"### Example" chunk repeats the same parameter names as the "### Parameters"
chunk it's paired with, and pulls rank away from it. Hit@5 doesn't see this because
both still land inside the top 5; average rank does.

Full per-question, per-rank dump for both strategies is in the console output —
see "Retrieval dump" below for the retry_backoff_ms example; the same shape holds
for all 8.

---

## 3. Metadata filter — unfiltered vs. filtered, one query, with scores

Query: **"What is the default value of retry_backoff_ms?"** against
`sdk_docs_structure`.

### Unfiltered

| Rank | Source | Version | Section | Distance |
|---|---|---|---|---|
| 1 | client_v2.md | v2 | Client.send() → Parameters | 0.4801 |
| 2 | client.md | v3 | Client.send() → Parameters | 0.6160 |
| 3 | client_v2.md | v2 | Client.send() → Example | 0.9823 |
| 4 | client.md | v3 | Client.send() → Example | 1.0136 |
| 5 | errors.md | v3 | ErrorHandler.configure() → Example | 1.0886 |

**Top-1 is the v2 page** (`retry_backoff_ms = 1000`) — this is the bug: the v3
answer (`500`) is correct but is outranked.

### Filtered (`sdk_version = v3`)

| Rank | Source | Version | Section | Distance |
|---|---|---|---|---|
| 1 | client.md | v3 | Client.send() → Parameters | 0.6160 |
| 2 | client.md | v3 | Client.send() → Example | 1.0136 |
| 3 | errors.md | v3 | ErrorHandler.configure() → Example | 1.0886 |
| 4 | errors.md | v3 | ErrorHandler.reset() | 1.1977 |
| 5 | errors.md | v3 | Errors API | 1.2935 |

With the filter applied, top-1 flips to the correct v3 page. The `client.md` /
`sdk_version=v3` chunk's own distance is unchanged (0.6160 in both runs) — filtering
restricts the candidate set before ranking, it doesn't re-embed or re-score.

---

## 4. Three cited answers (generation), chunk_ids verified to resolve

All three go through `app.services.rag.answer_question`, so citations come from Chroma's own
returned metadata/ids — never invented by the LLM.

**Q: "What is the default page_size for Pagination.configure()?"**
> The default `page_size` for `Pagination.configure()` is **50**.

Sources: `chunk_id=pagination-v3-2` → `pagination.md` → *Pagination.configure() →
Parameters*. Chunk content (verified): `| page_size | int | 50 | no |` +
"The `page_size` parameter controls the number of records requested per page."

**Q: "Is api_key required for Authentication.configure()?"**
> Yes, the `api_key` parameter is required when calling `Authentication.configure()`.
> The documentation's parameters table lists `api_key` with **Required: yes**.

Sources: `chunk_id=authentication-v3-2` → `authentication.md` → *Authentication.configure()
→ Parameters*. Chunk content (verified): `| api_key | string | none | yes |`.

**Q: "What is the default value of retry_backoff_ms?" (filtered, sdk_version=v3)**
> The default value of `retry_backoff_ms` is **500**.

Sources: `chunk_id=client-v3-2` → `client.md` → *Client.send() → Parameters*. Chunk
content (verified): `| retry_backoff_ms | int | 500 | no |`.

All three chunk_ids were independently fetched from `sdk_docs_structure` by id and
confirmed to contain the cited value (see "Retrieval dump" section).

---

## 5. Three refusal transcripts (out-of-corpus questions)

Run through the same `app.services.rag.answer_question` pipeline — the refusal is forced by
a distance threshold (`> 0.8` → refuse before the LLM is even called), not left to
the model's judgment.

```
Q: What is the default cache size for the Acme SDK?
Best retrieval distance: 1.1785
A: I don't know based on the provided documents.
Sources: (none — refused)

Q: What is the maximum number of concurrent requests supported?
Best retrieval distance: 1.0026
A: I don't know based on the provided documents.
Sources: (none — refused)

Q: What is the monthly price of the Acme SDK?
Best retrieval distance: [threshold exceeded]
A: I don't know based on the provided documents.
Sources: (none — refused)
```

No fabricated parameter, price, or limit was returned for any of the three.

---

## 6. Which chunker ships, and why

**The structure-aware chunker ships.** Hit@5 ties 8/8 with the simple chunker on
this small corpus, so hit@5 alone doesn't justify it — but two things do:
(1) it never splits a code fence or a parameter row from its header, which the
simple 300-char sliding window does by construction (it cuts mid-line wherever the
character count lands, regardless of markdown structure); (2) it's the only
strategy that produces a non-empty `section` for citations, which requirement 5
needs for "page + anchor." The simple chunker has no notion of section boundaries,
so its citations can only ever say "page: client, section: (blank)."

**The retrieval that embarrassed us:** we expected the structure-aware chunker to
also win on retrieval quality, since it produces cleaner, more semantically coherent
chunks. Instead it has a *worse* average rank for the correct chunk (1.875 vs
1.25) and a third as many rank-1 hits (2/8 vs 6/8, §2). **Diagnosis:** splitting on
every header level (including `###` subsections) doubled the chunk count (40 vs 20),
and sibling chunks under the same `##` section (e.g. "### Parameters" and
"### Example") repeat the same parameter names, so they compete with each other for
top rank instead of one chunk cleanly winning. Precision about section boundaries
came at the cost of retrieval sharpness. This didn't change which chunker ships
(hit@5 is what's graded, and citations need `section`), but it's a real tradeoff
worth knowing before assuming "more structure-aware" always means "retrieves
better."

---

## 7. Retrieval dump — retry_backoff_ms, both strategies, ranks 1–5

### Simple chunker (overlap=50)
```
Rank 1: client.md      distance=0.4353  contains_answer=True
Rank 2: client_v2.md   distance=0.6587  contains_answer=False
Rank 3: errors.md      distance=0.8627  contains_answer=False
Rank 4: client_v2.md   distance=0.9819  contains_answer=False
Rank 5: client.md      distance=1.0227  contains_answer=True
```

### Structure-aware chunker
```
Rank 1: client_v2.md section='Client.send() → Parameters' distance=0.4801 contains_answer=False
Rank 2: client.md    section='Client.send() → Parameters' distance=0.6160 contains_answer=True
Rank 3: errors.md    section='ErrorHandler.configure() → Parameters' distance=0.7661 contains_answer=False
Rank 4: client_v2.md section='Client.send() → Example'    distance=0.9823 contains_answer=False
Rank 5: client.md    section='Client.send() → Example'    distance=1.0136 contains_answer=True
```

Full 8-question × 2-strategy dump is reproducible via
`python -m app.scripts.evaluate_retrieval` (run with `PYTHONIOENCODING=utf-8` on
Windows, since section names contain `→`).

---

## 8. Code diff

The original chunker rewrite (section-tracking, `chunk_id` in citations) prior to
the restructure in §10 is saved as `code_diff_week4.patch` in the repo root. After
the restructure, the same logic lives at these (new) paths — full history is in
git via `git log --follow`:

- `app/services/chunker.py` — `structure_aware_chunk` tracks the nearest H1/H2/H3
  headings and tags every chunk with a `section` (e.g. `"Client.send() →
  Parameters"`), fixing empty `section` metadata that broke citations. Also now
  supports optional overlap on both chunkers (§10).
- `app/services/rag.py` — citations include `chunk_id` (from Chroma's own
  `results["ids"]`), so a citation resolves to a specific, fetchable chunk, not
  just a filename.
- `app/core/vector_store.py` — `add_chunks` uses `upsert` instead of `add`, so
  re-ingestion to refresh metadata doesn't fail on existing ids.
- `app/scripts/evaluate_retrieval.py` — hit@5 now requires the retrieved chunk to
  actually contain the expected answer text (not just come from the right file).
- `app/scripts/test_grounding.py` — now calls `app.services.rag.answer_question`
  (the real pipeline with the forced distance-threshold refusal) instead of
  duplicating the retrieval+generation logic without the refusal check.

---

## 9. Bonus challenge — precision vs. completeness

Query: **"How do I enable compression when creating a request?"**, single-chunk
retrieval (`n_results=1`) against `requests.md`, to expose what happens when only
the top chunk is handed to the model.

**Structure-aware chunker** — wins on retrieval. Distance 0.5552 vs. simple
chunker's 0.7861, and the retrieved chunk is exactly on-topic
(`Request.create() → Parameters`):
```
### Parameters

| Name        | Type   | Default | Required |
|-------------|--------|---------|----------|
| method      | string | GET     | yes      |
| timeout     | int    | 30      | no       |
| compression | bool   | true    | no       |

The `compression` parameter enables response compression for the request.
```
No code fence — the `### Example` section is a separate chunk that didn't make
the top-1 cut.

**Simple chunker** — its 300-char sliding window happens to straddle the table
*and* the code fence in one blob, so the example survives by accident of chunk
boundary, not by design.

**Answers, side by side:**

| Simple chunker (chunk had the code) | Structure-aware chunker (chunk had no code) |
|---|---|
| Enable compression by passing the `compression=True` argument when you create the request with `Request.create`. For example:<br>`request = Request.create(method="GET", timeout=30, compression=True)` | To enable compression, pass the `compression` parameter as `true` when you create the request:<br>`request = Request.create(method="GET", # or any HTTP method you need, timeout=30, # optional, compression=True # enable response compression)` |

The simple chunker's answer is a faithful quote of the real example. The
structure-aware answer's code block is **not** — it was synthesized from the
parameter table's default values (which is why it happens to match), and the
inline comments (`# or any HTTP method you need`, `# optional`) aren't in the
docs at all. It only looked right because the defaults matched the real example;
if the real usage pattern differed from "pass each parameter as its default,"
this would be silently wrong and no different from a real citation.

**The tension, in two sentences:** the tighter, structure-aware chunk retrieves
with lower distance and better topical precision, but strips away the
completeness a full answer needs — and the model doesn't visibly degrade or
refuse in response, it quietly reconstructs a plausible-looking substitute from
whatever fields it does have. That's worse than an incomplete answer: an
incomplete answer is visibly incomplete, while a fabricated-but-plausible one is
indistinguishable from a grounded citation unless someone checks the source chunk.

---

## 10. Engineering follow-ups: overlap, folder structure, chat UI

### 10.1 Chunk overlap — and a regression it caused

Overlap was added to both chunkers, but they needed opposite defaults:

- **Simple chunker** (`simple_chunk(text, chunk_size=300, overlap=50)`): a real
  sliding window now, stride = `chunk_size - overlap`. This chunker cuts at fixed
  character offsets regardless of sentence or table boundaries, so overlap
  genuinely helps recover context lost at a cut. Shipped default: `overlap=50`.
  Effect: Q5's rank improved from 2 to 1 (§2), rank-1 hits went from 5/8 to 6/8.

- **Structure-aware chunker** (`structure_aware_chunk(..., overlap_chars=0)`):
  tried the same idea — prepend the previous chunk's trailing text — and it
  **broke a previously-correct answer**. With `overlap_chars=100`, the filtered
  query "What is the default value of retry_backoff_ms?" (`sdk_version=v3`) went
  from distance 0.6160 to 0.8029 — just over the 0.8 refusal threshold — because
  the tight "### Parameters" chunk got diluted with unrelated boilerplate from
  the *previous* section ("## Client.send()\n\nSends an HTTP request..."). A
  previously-answerable question started getting wrongly refused. Sweeping
  `overlap_chars` from 0 to 100 showed even 25 characters was enough to flip the
  top-1 result to the wrong source file. **Diagnosis:** structure-aware chunks
  are already complete, header-bounded sections — there's no mid-sentence cut
  for overlap to repair, so it only adds noise. Shipped default: `overlap_chars=0`
  (the parameter is still there for a corpus with longer sections, where a chunk
  really could end mid-thought). This is caught and fixed — the live app was
  re-verified back at distance 0.6160 after the fix, and the full hit@5 suite
  re-run (§2 reflects the corrected numbers).

### 10.2 Folder structure

`app/` was reorganized from a flat directory into a layered package:

```
app/
  main.py              — FastAPI app creation + static mount
  api/routes.py         — the three endpoints (/, /upload, /ask)
  core/                 — config, embeddings, vector_store, loader, document_loader
  services/             — chunker, ingestion_service, rag, generator
  scripts/              — evaluate_retrieval, filter_test, test_grounding,
                           ingest_simple, ingest_structure, chat, test_groq,
                           evaluation_questions
  static/, templates/    — unchanged
```

Two dead/broken standalone scripts (`ingest.py`, `search.py` — both imported a
`collection` variable that no longer exists in `vector_store.py`, and neither
could actually run) were removed rather than moved.

Run commands changed for anything under `scripts/` — they're package modules now,
run with `-m` from the repo root:

```
uvicorn app.main:app --reload --port 5000      # unchanged
python -m app.scripts.ingest_simple
python -m app.scripts.ingest_structure
python -m app.scripts.evaluate_retrieval
python -m app.scripts.filter_test
python -m app.scripts.test_grounding
python -m app.scripts.chat
```

### 10.3 Centralized configuration + pipeline cleanup

Every previously-hardcoded, scattered value now lives in one place,
`app/core/config.py`, as a frozen `Settings` dataclass: embedding model name,
Chroma path and collection names, chunk size/overlap for both chunkers,
retrieval `top_k`, the refusal distance threshold, ingestion defaults
(`sdk_version`, `page_type`), allowed upload extensions, the Groq model name
and temperature, and the refusal message string itself (previously duplicated
as a literal in both `rag.py`'s hard threshold check and `generator.py`'s
prompt — now one string referenced from both, so they can't drift out of
sync). `.env` loading also moved here, so it happens exactly once instead of
being re-triggered by whichever module imported first. The `groq_api_key`
field is declared `repr=False` so it can never leak into a traceback, log
line, or a stray `print(settings)`.

`app/services/chunker.py` was split into single-purpose pieces —
`_is_code_fence_marker`, `_parse_heading`, a `_SectionTracker` class, and
`_split_into_sections` — instead of one function juggling fence-tracking,
header-parsing, and section-labeling in a single loop. Behavior is unchanged
(re-ingesting produced the identical 20/40 chunk counts and 8/8 hit@5 numbers
throughout §2).

`app/services/rag.py` was restructured from one long, numbered-comment
function into named steps (`_retrieve`, `_is_relevant_enough`,
`_build_context`, `_build_sources`) returning a `NamedTuple` (`AnswerResult`)
instead of a bare tuple — still unpacks as `answer, sources = ...` everywhere
that calls it, so nothing downstream broke, but the pipeline's stages are now
each independently readable and testable.

### 10.4 Chat UI

The frontend changed from a single-shot "form → replace last answer" page to a
multi-turn chat: questions and answers stack as bubbles in one scrolling thread
instead of overwriting each other, answers render markdown (bold, inline code,
code fences, lists) instead of plain text, and each assistant message shows its
own citations as collapsible chips (`chunk_id` / page / section) rather than one
shared sources panel for the whole page. "New chat" clears the thread. This is a
UI-only change — no new backend behavior, and it isn't part of the graded rubric
above, but it makes the citation-per-message requirement (§4) actually visible in
normal use instead of only in the API response.
