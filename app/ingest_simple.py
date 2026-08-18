from config import DOCUMENTS
from loader import load_document
from chunker import simple_chunk
from embeddings import create_embedding
from vector_store import simple_collection, add_chunks


all_chunks = []
all_embeddings = []


for document_info in DOCUMENTS:

    document = load_document(
        f"data/docs/{document_info['file']}"
    )

    raw_chunks = simple_chunk(
        document,
        chunk_size=300,
    )

    for chunk_number, chunk_text in enumerate(raw_chunks):

        chunk = {
            "chunk_id": f"{document_info['page_id']}-simple-{chunk_number}",
            "text": chunk_text,
            "metadata": {
                "source_file": document_info["file"],
                "page_id": document_info["page_id"],
                "sdk_version": document_info["sdk_version"],
                "page_type": document_info["page_type"],
            },
        }

        all_chunks.append(chunk)

        vector = create_embedding(chunk_text)

        all_embeddings.append(vector)


add_chunks(
    simple_collection,
    all_chunks,
    all_embeddings,
)


print(f"Indexed {len(all_chunks)} simple chunks")