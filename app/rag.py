from app.embeddings import create_embedding
from app.vector_store import structure_collection
from app.generator import generate_answer
import os 
from dotenv import load_dotenv

load_dotenv()

retkey=0.8


def answer_question(question, sdk_version=None):

    # 1. Convert the question into an embedding.
    query_vector = create_embedding(question)

    # 2. Search the vector database.
    if sdk_version:

        results = structure_collection.query(
            query_embeddings=[query_vector],
            n_results=5,
            where={
                "sdk_version": sdk_version,
            },
        )

    else:

        results = structure_collection.query(
            query_embeddings=[query_vector],
            n_results=5,
        )
    # 3. Get retrieved documents.
    documents = results["documents"][0]

    # 4. Get metadata.
    metadatas = results["metadatas"][0]

    # 5. Get similarity distances.
    distances = results["distances"][0]

    # 6. The first result is the closest result.
    best_distance = distances[0]

    print("\nBest retrieval distance:", best_distance)

    # 7. Check whether the best result is relevant enough.
    if best_distance > retkey:

        return (
            "I don't know based on the provided documents.",
            [],
        )

    # 8. Build the context for the LLM.
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

    # 9. Combine the retrieved chunks.
    context = "\n\n".join(context_parts)

    # 10. Ask Groq for a grounded answer.
    answer = generate_answer(
        question=question,
        context=context,
    )

    # 11. Build source information.
    sources = []

    for metadata in metadatas:

        source = {
            "source_file": metadata["source_file"],
            "page_id": metadata["page_id"],
            "section": metadata.get("section", ""),
        }

        if source not in sources:
            sources.append(source)

    # 12. Return answer + sources.
    return answer, sources