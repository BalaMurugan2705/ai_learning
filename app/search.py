from embeddings import create_embedding
from vector_store import collection


question = "What is the default value of retry_backoff_ms?"


query_vector = create_embedding(question)


results = collection.query(
    query_embeddings=[query_vector],
    n_results=3,
)


for index, document in enumerate(results["documents"][0]):
    print("\n====================")
    print(f"RESULT {index + 1}")
    print("====================")

    print("DOCUMENT:")
    print(document)

    print("\nMETADATA:")
    print(results["metadatas"][0][index])

    print("\nDISTANCE:")
    print(results["distances"][0][index])