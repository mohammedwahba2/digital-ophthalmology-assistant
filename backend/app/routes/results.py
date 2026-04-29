from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.prediction import Prediction

router = APIRouter(prefix="/api/v1", tags=["results"])


@router.get("/results/{id}")
def get_result(id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Result not found")

    return {
        "id": record.id,
        "image_path": record.image_path,
        "prediction": record.prediction,
        "confidence": record.confidence,
        "created_at": record.created_at,
    }


@router.get("/results")
def list_results(
    min_confidence: Optional[float] = Query(default=None, ge=0.0, le=1.0),
    prediction: Optional[str] = Query(default=None),
    date_from: Optional[datetime] = Query(default=None),
    date_to: Optional[datetime] = Query(default=None),
    page: int = Query(default=1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Number of results per page"),
    db: Session = Depends(get_db),
):
    """List prediction results with pagination support.
    
    Returns paginated results to handle large datasets efficiently.
    Maximum page_size is 100 to prevent excessive memory usage.
    """
    query = db.query(Prediction)

    if min_confidence is not None:
        query = query.filter(Prediction.confidence >= min_confidence)
    if prediction is not None and prediction.strip():
        query = query.filter(Prediction.prediction == prediction.strip())
    if date_from is not None:
        query = query.filter(Prediction.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Prediction.created_at <= date_to)

    # Get total count for pagination metadata
    total_count = query.count()
    
    # Apply pagination
    offset = (page - 1) * page_size
    records = query.order_by(Prediction.created_at.desc()).offset(offset).limit(page_size).all()
    
    return {
        "data": [
            {
                "id": r.id,
                "image_path": r.image_path,
                "prediction": r.prediction,
                "confidence": r.confidence,
                "created_at": r.created_at,
            }
            for r in records
        ],
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total_count": total_count,
            "total_pages": (total_count + page_size - 1) // page_size,
            "has_next": offset + page_size < total_count,
            "has_previous": page > 1,
        }
    }


@router.delete("/results/{id}")
def delete_result(id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Result not found")

    db.delete(record)
    db.commit()
    return {"deleted": True, "id": id}
