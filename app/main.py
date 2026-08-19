from fastapi import FastAPI, UploadFile, File
from app.rag import answer_question
from app.ingestion_service import ingest_document
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pathlib import Path
from app.document_loader import load_uploaded_document

app = FastAPI()

ALLOWED_EXTENSIONS = {
    ".md",
    ".txt",
     ".pdf",
}

class QuestionRequest(BaseModel):

    question: str

    sdk_version: str | None = None
BASE_DIR = Path(__file__).resolve().parent

app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static",
)
@app.get(
    "/",
    response_class=HTMLResponse,
)
def home():

    html_file = (
        BASE_DIR
        / "templates"
        / "index.html"
    )

    return html_file.read_text(
        encoding="utf-8"
    )

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:

        return {
            "error": (
                "Unsupported file type. "
                "Please upload .md or .txt files."
            )
        }

    content = await file.read()

    text = load_uploaded_document(
        filename=file.filename,
        content=content,
    )

    chunk_count = ingest_document(
        filename=file.filename,
        text=text,
    )

    return {
        "filename": file.filename,
        "chunks_indexed": chunk_count,
        "message": "Document ingested successfully.",
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    answer, sources = answer_question(
        request.question,
        sdk_version=request.sdk_version,
    )

    return {
        "answer": answer,
        "sources": sources,
    }