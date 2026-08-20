"""Plain data types shared across interfaces and services."""
from typing import NamedTuple


class RetrievedChunk(NamedTuple):
    chunk_id: str
    text: str
    metadata: dict
    distance: float


class AnswerResult(NamedTuple):
    answer: str
    sources: list
