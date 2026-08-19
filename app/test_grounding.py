from embeddings import create_embedding
from vector_store import structure_collection
from generator import generate_answer


QUESTIONS = [
    {
        "id": "Q1",
        "question": "What is the default value of retry_backoff_ms?",
        "type": "answerable",
    },
    {
        "id": "Q2",
        "question": "What is the default page_size for Pagination.configure()?",
        "type": "answerable",
    },
    {
        "id": "Q3",
        "question": "Is api_key required for Authentication.configure()?",
        "type": "answerable",
    },
    {
        "id": "Q4",
        "question": "What is the default cache size for the Acme SDK?",
        "type": "unanswerable",
    },
    {
        "id": "Q5",
        "question": "What is the maximum number of concurrent requests supported?",
        "type": "unanswerable",
    },
    {
        "id": "Q6",
        "question": "What is the monthly price of the Acme SDK?",
        "type": "unanswerable",
    },
]


for item in QUESTIONS:

    question = item["question"]

    query_vector = create_embedding(question)

    results = structure_collection.query(
        query_embeddings=[query_vector],
        n_results=5,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    best_distance = distances[0]

    context_parts = []

    for document, metadata in zip(documents, metadatas):

        context_parts.append(
            f"""
SOURCE FILE: {metadata['source_file']}
PAGE: {metadata['page_id']}
SECTION: {metadata.get('section', '')}

{document}
"""
        )

    context = "\n\n".join(context_parts)

    answer = generate_answer(
        question=question,
        context=context,
    )

    print("\n" + "=" * 70)
    print(item["id"])
    print("=" * 70)

    print("Type:", item["type"])
    print("Question:", question)
    print("Best distance:", best_distance)
    print("Answer:", answer)