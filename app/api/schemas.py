from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(..., min_length=1)
    sdk_version: str | None = None


class Source(BaseModel):
    chunk_id: str
    source_file: str
    page_id: str
    section: str = ""


class AskResponse(BaseModel):
    answer: str
    sources: list[Source]


class UploadResponse(BaseModel):
    filename: str
    chunks_indexed: int
    message: str
