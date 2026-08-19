from fastapi import FastAPI, UploadFile, File

from ingestion_service import ingest_document


app = FastAPI()


@app.get("/")
def home():

    return {
        "message": "Ask My Documents API is running"
    }


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    content = await file.read()

    text = content.decode("utf-8")

    chunk_count = ingest_document(
        filename=file.filename,
        text=text,
    )

    return {
        "filename": file.filename,
        "chunks_indexed": chunk_count,
    }