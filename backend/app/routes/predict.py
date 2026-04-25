import uuid
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.prediction import Prediction
from app.services.ai_service import predict_image

router = APIRouter(tags=["predict"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/predict")
async def run_prediction(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        with Image.open(BytesIO(content)) as img:
            img.verify()
    except (UnidentifiedImageError, OSError, SyntaxError):
        raise HTTPException(status_code=400, detail="Invalid image file") from None

    file_path = UPLOAD_DIR / f"{uuid.uuid4()}{suffix}"
    file_path.write_bytes(content)

    try:
        label, confidence = predict_image(str(file_path))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from None

    record = Prediction(
        image_path=str(file_path),
        prediction=label,
        confidence=confidence,
    )
    db.add(record)
    db.commit()

    return {
        "label": label,
        "confidence": confidence,
    }
