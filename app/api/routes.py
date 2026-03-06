from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates

from app.core.config import (
    ALLOWED_IMAGE_EXTENSIONS,
    TEMPLATES_DIR,
    UPLOAD_DIR,
)
from app.services.analyzer import analyze_car_image

router = APIRouter()
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )


@router.post("/predict")
async def predict(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Không có file được upload.")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File không hợp lệ. Chỉ chấp nhận: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    unique_name = f"{uuid.uuid4()}{ext}"
    save_path = UPLOAD_DIR / unique_name

    try:
        with save_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = analyze_car_image(str(save_path))

        return JSONResponse({
            "success": True,
            "filename": unique_name,
            "result": result
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý ảnh: {str(e)}")