"""VectorStore adapter backed by Chroma. Callers only ever see
`RetrievedChunk` objects — chromadb's own parallel-list result shape
(`results["ids"][0]`, `results["documents"][0]`, ...) never leaks past
this module."""
from typing import Optional

import chromadb

from app.core.models import RetrievedChunk


def build_chroma_client(path: str):
    return chromadb.PersistentClient(path=path)


class ChromaVectorStore:
    def __init__(self, client, collection_name: str):
        self._collection = client.get_or_create_collection(name=collection_name)

    def upsert(self, chunks: list[dict], embeddings: list[list[float]]) -> None:
        self._collection.upsert(
            ids=[chunk["chunk_id"] for chunk in chunks],
            documents=[chunk["text"] for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk["metadata"] for chunk in chunks],
        )

    def query(
        self,
        query_embedding: list[float],
        top_k: int,
        where: Optional[dict] = None,
    ) -> list[RetrievedChunk]:
        results = self._collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
        )

        return [
            RetrievedChunk(chunk_id=chunk_id, text=document, metadata=metadata, distance=distance)
            for chunk_id, document, metadata, distance in zip(
                results["ids"][0],
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            )
        ]
