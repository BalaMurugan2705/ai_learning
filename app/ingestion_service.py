from chunker import structure_aware_chunk
from embeddings import create_embedding
from vector_store import structure_collection


def ingest_document(
    filename,
    text,
    sdk_version="v3",
    page_type="reference",
):

    page_id = filename.rsplit(".", 1)[0]

    chunks = structure_aware_chunk(
        text=text,
        source_file=filename,
        page_id=page_id,
        sdk_version=sdk_version,
        page_type=page_type,
    )

    embeddings = []

    for chunk in chunks:

        vector = create_embedding(
            chunk["text"]
        )

        embeddings.append(vector)

    ids = []

    documents = []

    metadatas = []

    for chunk in chunks:

        ids.append(chunk["chunk_id"])

        documents.append(
            chunk["text"]
        )

        metadatas.append(
            chunk["metadata"]
        )

    structure_collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )

    return len(chunks)