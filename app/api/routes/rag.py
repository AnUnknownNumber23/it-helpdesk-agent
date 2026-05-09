import errno
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.core.config import settings
from app.schemas.rag import AskRequest, AskResponse, IngestResponse
from app.services.ingest_service import ingest_file
from app.services.query_service import answer_question


router = APIRouter(prefix="/rag", tags=["rag"])
INVALID_PATH_ERRNOS = {
    errno.EACCES,
    errno.EPERM,
    errno.EEXIST,
    errno.ENOTDIR,
    errno.EISDIR,
    errno.EROFS,
    errno.EINVAL,
}


@router.post("/ask", response_model=AskResponse)
def ask_question(request: AskRequest) -> AskResponse:
    return answer_question(request.question, request.top_k)


@router.post(
    "/ingest",
    response_model=IngestResponse,
    openapi_extra={"requestBody": {"required": True}},
)
async def ingest(file: UploadFile | None = File(None)) -> IngestResponse:
    if file is None or not file.filename:
        raise HTTPException(status_code=400, detail="Missing file name.")
    if Path(file.filename).suffix.lower() != ".md":
        raise HTTPException(status_code=400, detail="Only .md files are supported.")

    try:
        upload_dir = Path(settings.upload_dir)
        upload_dir.mkdir(parents=True, exist_ok=True)
        saved_path = upload_dir / Path(file.filename).name
        saved_path.write_bytes(await file.read())
        result = ingest_file(saved_path)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found.")
    except (PermissionError, IsADirectoryError, NotADirectoryError):
        raise HTTPException(status_code=400, detail="Invalid file path.")
    except OSError as exc:
        if exc.errno in INVALID_PATH_ERRNOS:
            raise HTTPException(status_code=400, detail="Invalid file path.")
        raise
    return IngestResponse(
        message="Ingestion completed.",
        file=result["file"],
        file_path=str(saved_path),
        chunks=result["chunks"],
    )
