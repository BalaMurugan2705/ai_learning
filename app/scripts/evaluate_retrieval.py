from app.core.dependencies import get_embedding_provider, get_simple_vector_store, get_structure_vector_store
from app.scripts.evaluation_questions import QUESTIONS


def evaluate_collection(vector_store, embedding_provider, strategy_name):

    print("\n")
    print("========================================")
    print(strategy_name)
    print("========================================")

    hits = 0
    per_question = []

    for item in QUESTIONS:

        question = item["question"]
        expected_answer = item["expected_answer"]
        expected_source = item["source_file"]

        query_vector = embedding_provider.embed(question)
        results = vector_store.query(query_vector, top_k=5)

        # A hit means: the chunk that actually contains the expected answer
        # text is present in the top 5 AND it comes from the expected page.
        # Matching on source_file alone is too coarse to tell chunkers apart
        # in a 6-7 document corpus — almost any query returns the right file.
        hit = False
        hit_rank = None

        for rank, chunk in enumerate(results, start=1):
            answer_present = expected_answer.lower() in chunk.text.lower()
            right_source = chunk.metadata["source_file"] == expected_source

            if answer_present and right_source:
                hit = True
                hit_rank = rank
                break

        if hit:
            hits += 1

        per_question.append(
            {
                "id": item["id"],
                "hit": hit,
                "hit_rank": hit_rank,
            }
        )

        print("\n----------------------------------------")
        print(item["id"])
        print(question)
        print(f"Expected answer substring: {expected_answer!r}")
        print(f"Expected source: {expected_source}")
        print(f"Hit@5 (chunk contains answer AND right source): {hit}"
              + (f" (rank {hit_rank})" if hit else ""))

        for rank, chunk in enumerate(results, start=1):
            contains_answer = expected_answer.lower() in chunk.text.lower()
            print(
                f"Rank {rank}: "
                f"{chunk.metadata['source_file']} "
                f"section={chunk.metadata.get('section', '')!r} "
                f"distance={chunk.distance:.4f} "
                f"contains_answer={contains_answer}"
            )

    print("\n========================================")
    print(f"{strategy_name} Hit@5 = {hits}/{len(QUESTIONS)}")
    print("Per-question:", {p["id"]: p["hit"] for p in per_question})
    print("========================================")

    return hits, per_question


embedding_provider = get_embedding_provider()

simple_hits, simple_per_question = evaluate_collection(
    get_simple_vector_store(),
    embedding_provider,
    "SIMPLE CHUNKER",
)


structure_hits, structure_per_question = evaluate_collection(
    get_structure_vector_store(),
    embedding_provider,
    "STRUCTURE-AWARE CHUNKER",
)

print("\n")
print("========================================")
print("SUMMARY")
print("========================================")
print(f"Simple chunker:          {simple_hits}/{len(QUESTIONS)}")
print(f"Structure-aware chunker: {structure_hits}/{len(QUESTIONS)}")
