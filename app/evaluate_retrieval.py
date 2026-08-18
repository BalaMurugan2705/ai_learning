from evaluation_questions import QUESTIONS
from embeddings import create_embedding
from vector_store import simple_collection, structure_collection


def evaluate_collection(collection, strategy_name):

    print("\n")
    print("========================================")
    print(strategy_name)
    print("========================================")

    hits = 0

    for item in QUESTIONS:

        question = item["question"]

        query_vector = create_embedding(question)

        results = collection.query(
            query_embeddings=[query_vector],
            n_results=5,
        )

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        expected_source = item["source_file"]

        hit = False

        for metadata in metadatas:

            if metadata["source_file"] == expected_source:
                hit = True
                break

        if hit:
            hits += 1

        print("\n----------------------------------------")
        print(item["id"])
        print(question)
        print(f"Expected source: {expected_source}")
        print(f"Hit@5: {hit}")

        for rank, (metadata, distance) in enumerate(
            zip(metadatas, distances),
            start=1,
        ):
            print(
                f"Rank {rank}: "
                f"{metadata['source_file']} "
                f"distance={distance}"
            )

    print("\n========================================")
    print(f"{strategy_name} Hit@5 = {hits}/8")
    print("========================================")


evaluate_collection(
    simple_collection,
    "SIMPLE CHUNKER",
)


evaluate_collection(
    structure_collection,
    "STRUCTURE-AWARE CHUNKER",
)