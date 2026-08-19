from embeddings import create_embedding
from vector_store import structure_collection


question = "What is the default value of retry_backoff_ms?"

query_vector = create_embedding(question)


def print_results(title, results):

    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)

    for rank, (document, metadata, distance) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ),
        start=1,
    ):

        print(f"\nRank {rank}")
        print(f"Source: {metadata['source_file']}")
        print(f"Version: {metadata['sdk_version']}")
        print(f"Section: {metadata.get('section', '')}")
        print(f"Distance: {distance}")

        print("\nText:")
        print(document)


unfiltered_results = structure_collection.query(
    query_embeddings=[query_vector],
    n_results=5,
)


filtered_results = structure_collection.query(
    query_embeddings=[query_vector],
    n_results=5,
    where={
        "sdk_version": "v3"
    },
)


print_results(
    "UNFILTERED SEARCH",
    unfiltered_results,
)


print_results(
    "FILTERED SEARCH — sdk_version=v3",
    filtered_results,
)