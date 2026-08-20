"""Two interchangeable ChunkingStrategy implementations for markdown SDK
reference pages — both take the same arguments and return the same chunk
shape, so RagService/IngestionService can use either without knowing which.

SimpleChunker is a naive fixed-width sliding window — a baseline that can
cut a parameter table or code fence in half wherever the character count
happens to land.

StructureAwareChunker splits on markdown headers, never splits inside a
code fence, and tags each chunk with the section (heading path) it belongs
to — so a table row and the header above it always stay in the same chunk.
"""


def _build_chunk(chunk_id, text, source_file, page_id, sdk_version, page_type, section=""):
    return {
        "chunk_id": chunk_id,
        "text": text,
        "metadata": {
            "source_file": source_file,
            "page_id": page_id,
            "sdk_version": sdk_version,
            "page_type": page_type,
            "section": section,
        },
    }


class SimpleChunker:
    def __init__(self, chunk_size: int, overlap: int):
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self._chunk_size = chunk_size
        self._overlap = overlap

    def chunk(self, text, *, source_file, page_id, sdk_version, page_type):
        stride = self._chunk_size - self._overlap
        raw_chunks = []
        start = 0

        while start < len(text):
            raw_chunks.append(text[start:start + self._chunk_size])

            if start + self._chunk_size >= len(text):
                break

            start += stride

        return [
            _build_chunk(
                chunk_id=f"{page_id}-{sdk_version}-simple-{number}",
                text=chunk_text,
                source_file=source_file,
                page_id=page_id,
                sdk_version=sdk_version,
                page_type=page_type,
            )
            for number, chunk_text in enumerate(raw_chunks)
        ]


def _is_code_fence_marker(line):
    return line.strip().startswith("```")


def _parse_heading(line):
    """Returns (level, heading_text) for a markdown header line, or None."""
    if not line.startswith("#"):
        return None

    level = len(line) - len(line.lstrip("#"))
    return level, line[level:].strip()


class _SectionTracker:
    """Tracks the nearest H1/H2/H3 headings while walking a document, so
    each chunk can be tagged with the section it falls under (e.g.
    "Client.send() → Parameters")."""

    def __init__(self):
        self._headers = {1: None, 2: None, 3: None}

    def update(self, level, heading_text):
        if level == 1:
            self._headers = {1: heading_text, 2: None, 3: None}
        elif level == 2:
            self._headers[2] = heading_text
            self._headers[3] = None
        else:
            self._headers[3] = heading_text

    @property
    def current_section(self):
        parts = [self._headers[level] for level in (2, 3) if self._headers[level]]
        if parts:
            return " → ".join(parts)
        return self._headers[1] or ""


def _split_into_sections(text):
    """Splits markdown into (text, section) blocks at each header line,
    without ever splitting inside a code fence."""
    lines = text.splitlines()
    sections = []
    current_lines = []
    inside_code_fence = False
    tracker = _SectionTracker()
    section_at_block_start = tracker.current_section

    for line in lines:
        if _is_code_fence_marker(line):
            inside_code_fence = not inside_code_fence
            current_lines.append(line)
            continue

        heading = None if inside_code_fence else _parse_heading(line)

        if heading:
            if current_lines:
                sections.append(("\n".join(current_lines), section_at_block_start))
                current_lines = []

            tracker.update(*heading)
            section_at_block_start = tracker.current_section

        current_lines.append(line)

    if current_lines:
        sections.append(("\n".join(current_lines), section_at_block_start))

    return sections


def _add_overlap(chunks, overlap_chars):
    """Prepends the trailing `overlap_chars` of each chunk's text onto the
    next one, so a chunk that opens mid-thought still carries some context
    from the section before it. Only adds text, never removes any — so it
    can't split a table row or code fence that `_split_into_sections`
    already kept intact.
    """
    if overlap_chars <= 0 or len(chunks) < 2:
        return chunks

    overlapped = [chunks[0]]

    for index in range(1, len(chunks)):
        previous_text, _ = chunks[index - 1]
        text, section = chunks[index]

        tail = previous_text[-overlap_chars:]
        overlapped.append((f"{tail}\n...\n{text}", section))

    return overlapped


class StructureAwareChunker:
    def __init__(self, overlap_chars: int = 0):
        self._overlap_chars = overlap_chars

    def chunk(self, text, *, source_file, page_id, sdk_version, page_type):
        sections = _split_into_sections(text)
        sections = _add_overlap(sections, self._overlap_chars)

        return [
            _build_chunk(
                chunk_id=f"{page_id}-{sdk_version}-{number}",
                text=chunk_text,
                source_file=source_file,
                page_id=page_id,
                sdk_version=sdk_version,
                page_type=page_type,
                section=section,
            )
            for number, (chunk_text, section) in enumerate(sections)
        ]
