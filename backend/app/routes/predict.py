"""Prediction endpoint for eye disease classification.

Handles image upload, validation, and ML inference with proper
error handling and database logging.
"""

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

router = APIRouter(tags=["predict"])


def _validate_image(content: bytes) -> Image.Image:
    """Validate and return image from bytes.

    Args:
        content: Raw image bytes.

    Returns:
        Validated PIL Image.

    Raises:
        HTTPException: If image is invalid or corrupted.
    """
    try:
        img = Image.open(BytesIO(content))
        img.verify()  # Verify it's a valid image
        # Re-open after verify (verify can leave image in bad state)
        img = Image.open(BytesIO(content))
        return img
    except (UnidentifiedImageError, OSError, SyntaxError) as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or corrupted image file",
        ) from e


@router.post(
    "/predict",
    response_model=dict[str, str | float],
    summary="Predict eye disease from image",
    description="Upload an eye image to get a disease prediction with confidence score.",
    responses={
        200: {"description": "Successful prediction"},
        400: {"description": "Invalid or missing image file"},
        413: {"description": "File too large"},
        415: {"description": "Unsupported file type"},
        500: {"description": "Internal server error during prediction"},
    },
)
async def run_prediction(
    file: UploadFile = File(
        ...,
        description="Eye image file (JPG, JPEG, PNG, BMP, or WEBP)",
    ),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict[str, str | float]:
    """Run prediction on uploaded eye image.

    Args:
        file: Uploaded image file.
        db: Database session.
        settings: Application settings.

    Returns:
        Dictionary with 'label' and 'confidence' keys.

    Raises:
        HTTPException: For various error conditions.
    """
    # Validate filename
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing filename in upload",
        )

    # Validate file extension
    suffix = Path(file.filename).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=f"Unsupported file extension '{suffix}'. Allowed: {settings.allowed_extensions}",
        )

    # Read file content
    content = await file.read()

    # Validate content is not empty
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file received",
        )

    # Check file size
    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum of {settings.max_upload_size_mb}MB",
        )

    # Validate image format
    _validate_image(content)

    # Generate unique filename and save
    file_path = settings.resolved_upload_dir / f"{uuid.uuid4()}{suffix}"
    settings.resolved_upload_dir.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(content)

    # Run prediction
    try:
        label, confidence = predict_image(str(file_path))
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed. Please try again.",
        ) from e

    # Log prediction to database
    record = Prediction(
        image_path=str(file_path),
        prediction=label,
        confidence=confidence,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "label": label,
        "confidence": round(confidence, 4),
    }