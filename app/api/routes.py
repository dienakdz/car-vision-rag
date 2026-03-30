from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.config import (
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    TEMPLATES_DIR,
    UPLOAD_DIR,
)
from app.services.analyzer import analyze_car_image

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def _validate_upload_size(file: UploadFile) -> None:
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    if file_size > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File qua lon. Gioi han toi da {MAX_FILE_SIZE_MB}MB.",
        )


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request},
    )


@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Khong co file duoc upload.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_IMAGE_EXTENSIONS))
        raise HTTPException(
            status_code=400,
            detail=f"File khong hop le. Chi chap nhan: {allowed}",
        )

    _validate_upload_size(file)

    unique_name = f"{uuid.uuid4()}{ext}"
    save_path = UPLOAD_DIR / unique_name

    try:
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = await run_in_threadpool(analyze_car_image, str(save_path))
        return JSONResponse(
            {
                "success": True,
                "filename": unique_name,
                "result": result,
            }
        )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Loi xu ly anh: {exc}") from exc
    finally:
        await file.close()
