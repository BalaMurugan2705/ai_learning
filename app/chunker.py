from app.loader import load_document


def simple_chunk(text, chunk_size=300):
    chunks = []

    for start in range(0, len(text), chunk_size):
        chunk = text[start:start + chunk_size]
        chunks.append(chunk)

    return chunks

def structure_aware_chunk(
    text,
    source_file,
    page_id,
    sdk_version,
    page_type,
):
    lines = text.splitlines()

    chunks = []
    current_chunk = []

    inside_code_fence = False

    for line in lines:

        is_code_fence = line.strip().startswith("```")

        if is_code_fence:
            inside_code_fence = not inside_code_fence
            current_chunk.append(line)
            continue

        is_header = line.startswith("#")

        if is_header and not inside_code_fence:

            if current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = []

        current_chunk.append(line)

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    result = []

    for chunk_number, chunk_text in enumerate(chunks):

        chunk = create_chunk(
            text=chunk_text,
            source_file=source_file,
            page_id=page_id,
            sdk_version=sdk_version,
            page_type=page_type,
            chunk_number=chunk_number,
        )

        result.append(chunk)

    return result

def create_chunk(text, source_file, page_id, sdk_version, page_type, chunk_number):
    return {
        "chunk_id": f"{page_id}-{sdk_version}-{chunk_number}",
        "text": text,
        "metadata": {
            "source_file": source_file,
            "page_id": page_id,
            "sdk_version": sdk_version,
            "page_type": page_type,
        },
    }