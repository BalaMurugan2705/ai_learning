from config import DOCUMENTS
from loader import load_document
from chunker import structure_aware_chunk
from embeddings import create_embedding
from vector_store import add_chunks


all_chunks = []
all_embeddings = []


for document_info in DOCUMENTS:

    document = load_document(
        f"data/docs/{document_info['file']}"
    )

    chunks = structure_aware_chunk(
        text=document,
        source_file=document_info["file"],
        page_id=document_info["page_id"],
        sdk_version=document_info["sdk_version"],
        page_type=document_info["page_type"],
    )

    all_chunks.extend(chunks)

    for chunk in chunks:
        vector = create_embedding(chunk["text"])
        all_embeddings.append(vector)


add_chunks(all_chunks, all_embeddings)


print(f"Indexed {len(all_chunks)} chunks")