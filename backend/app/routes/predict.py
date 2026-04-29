"""Prediction endpoint for eye disease classification.

Handles image upload, validation, and DL inference with proper
error handling and database logging. Implements the preprocessing
pipeline described in the project methodology, including the custom
Center Crop algorithm for ocular focus.
"""

import logging
import uuid
from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError
from sqlalchemy.orm import Session

from app.config import get_settings, Settings
from app.database.db import get_db
from app.models.prediction import Prediction
from app.services.ai_service import predict_image

logger = logging.getLogger(__name__)

# Image dimension constraints
MIN_IMAGE_DIMENSION = 50  # Minimum width/height in pixels
MAX_IMAGE_DIMENSION = 4096  # Maximum width/height in pixels

router = APIRouter(tags=["predict"])


def _validate_image(content: bytes) -> Image.Image:
    """Validate and return image from bytes.
    
    Performs comprehensive validation including:
    - File format verification
    - Dimension constraints check
    - Image integrity verification
    
    Returns:
        Validated PIL Image instance.
    
    Raises:
        HTTPException: If image is invalid, corrupted, or outside dimension limits.
    """
    try:
        img = Image.open(BytesIO(content))
        img.verify()
        img = Image.open(BytesIO(content))
        
        # Validate image dimensions
        width, height = img.size
        if width < MIN_IMAGE_DIMENSION or height < MIN_IMAGE_DIMENSION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image dimensions too small ({width}x{height}). Minimum: {MIN_IMAGE_DIMENSION}x{MIN_IMAGE_DIMENSION}",
            )
        if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Image dimensions too large ({width}x{height}). Maximum: {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}",
            )
        
        return img
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, SyntaxError) as e:
        logger.error(f"Image validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted image file",
        ) from e


@router.post(
    "/predict",
    response_model=dict[str, str | float],
    summary="Predict eye disease from image",
)
async def run_prediction(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, str | float]:

    # -------------------------
    # 1. Validate file
    # -------------------------
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing filename in upload",
        )

    suffix = Path(file.filename).suffix.lower()

    if suffix not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file type: {suffix}",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file received",
        )

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large",
        )

    # -------------------------
    # 2. Validate image
    # -------------------------
    _validate_image(content)

    # -------------------------
    # 3. Save file
    # -------------------------
    upload_dir = settings.resolved_upload_dir
    upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = upload_dir / f"{uuid.uuid4()}{suffix}"
    file_path.write_bytes(content)

    # -------------------------
    # 4. Prediction (DL MODEL)
    # -------------------------
    try:
        label, confidence = predict_image(file_path)
        logger.info(f"Prediction completed: {label} ({confidence:.4f})")
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Model not found. Please ensure the model is properly deployed.",
        )
    except ValueError as e:
        logger.error(f"Invalid input for prediction: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Prediction error: {str(e)}",
        )
    except Exception as e:
        logger.error(f"Unexpected prediction error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed due to an internal error",
        )

    # -------------------------
    # 5. Save to DB
    # -------------------------
    record = Prediction(
        image_path=str(file_path),
        prediction=label,
        confidence=confidence,
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    # -------------------------
    # 6. Response
    # -------------------------
    return {
        "label": label,
        "confidence": round(confidence, 4),
    }