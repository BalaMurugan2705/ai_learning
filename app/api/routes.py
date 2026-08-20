from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import HTMLResponse

from app.api.schemas import AskResponse, QuestionRequest, UploadResponse
from app.core.config import settings
from app.core.dependencies import get_ingestion_service, get_rag_service, get_text_extractor
from app.infrastructure.document_extractors import ExtensionBasedTextExtractor
from app.services.ingestion_service import IngestionService
from app.services.rag_service import RagService

router = APIRouter()

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"


@router.get("/", response_class=HTMLResponse)
def home():
    return (TEMPLATES_DIR / "index.html").read_text(encoding="utf-8")


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    text_extractor: ExtensionBasedTextExtractor = Depends(get_text_extractor),
    ingestion_service: IngestionService = Depends(get_ingestion_service),
):
    extension = Path(file.filename).suffix.lower()

    if extension not in settings.allowed_upload_extensions:
        allowed = ", ".join(sorted(settings.allowed_upload_extensions))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{extension}'. Allowed types: {allowed}.",
        )

    content = await file.read()

    try:
        text = text_extractor.extract_from_filename(file.filename, content)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error

    if not text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no extractable text.",
        )

    chunk_count = ingestion_service.ingest(
        filename=file.filename,
        text=text,
        sdk_version=settings.default_sdk_version,
        page_type=settings.default_page_type,
    )

    return UploadResponse(
        filename=file.filename,
        chunks_indexed=chunk_count,
        message="Document ingested successfully.",
    )


@router.post("/ask", response_model=AskResponse)
def ask_question(
    request: QuestionRequest,
    rag_service: RagService = Depends(get_rag_service),
):
    answer, sources = rag_service.answer(request.question, sdk_version=request.sdk_version)
    return AskResponse(answer=answer, sources=sources)
