from app.core.config import DOCUMENTS, settings
from app.core.dependencies import get_embedding_provider, get_simple_vector_store
from app.core.document_loader import load_document
from app.services.chunking import SimpleChunker

chunker = SimpleChunker(settings.simple_chunk_size, settings.simple_chunk_overlap)
embedding_provider = get_embedding_provider()
vector_store = get_simple_vector_store()

all_chunks = []
all_embeddings = []


for document_info in DOCUMENTS:

    document = load_document(
        f"data/docs/{document_info['file']}"
    )

    chunks = chunker.chunk(
        document,
        source_file=document_info["file"],
        page_id=document_info["page_id"],
        sdk_version=document_info["sdk_version"],
        page_type=document_info["page_type"],
    )

    all_chunks.extend(chunks)

    for chunk in chunks:
        all_embeddings.append(
            embedding_provider.embed(chunk["text"])
        )


vector_store.upsert(all_chunks, all_embeddings)


print(f"Indexed {len(all_chunks)} simple chunks")
