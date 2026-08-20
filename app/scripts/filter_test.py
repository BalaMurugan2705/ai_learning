from app.core.dependencies import get_embedding_provider, get_structure_vector_store

question = "What is the default value of retry_backoff_ms?"

embedding_provider = get_embedding_provider()
vector_store = get_structure_vector_store()

query_vector = embedding_provider.embed(question)


def print_results(title, chunks):

    print("\n")
    print("=" * 60)
    print(title)
    print("=" * 60)

    for rank, chunk in enumerate(chunks, start=1):

        print(f"\nRank {rank}")
        print(f"Source: {chunk.metadata['source_file']}")
        print(f"Version: {chunk.metadata['sdk_version']}")
        print(f"Section: {chunk.metadata.get('section', '')}")
        print(f"Distance: {chunk.distance}")

        print("\nText:")
        print(chunk.text)


unfiltered_results = vector_store.query(query_vector, top_k=5)


filtered_results = vector_store.query(
    query_vector,
    top_k=5,
    where={"sdk_version": "v3"},
)


print_results(
    "UNFILTERED SEARCH",
    unfiltered_results,
)


print_results(
    "FILTERED SEARCH — sdk_version=v3",
    filtered_results,
)
