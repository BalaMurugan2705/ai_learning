import chromadb


client = chromadb.PersistentClient(path="./chroma_db")


simple_collection = client.get_or_create_collection(
    name="sdk_docs_simple"
)


structure_collection = client.get_or_create_collection(
    name="sdk_docs_structure"
)


def add_chunks(collection, chunks, embeddings):
    ids = []
    documents = []
    metadatas = []

    for chunk, embedding in zip(chunks, embeddings):
        ids.append(chunk["chunk_id"])
        documents.append(chunk["text"])
        metadatas.append(chunk["metadata"])

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
    )