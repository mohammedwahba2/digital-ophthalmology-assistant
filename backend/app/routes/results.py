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
    db: Session = Depends(get_db),
):
    query = db.query(Prediction)

    if min_confidence is not None:
        query = query.filter(Prediction.confidence >= min_confidence)
    if prediction is not None and prediction.strip():
        query = query.filter(Prediction.prediction == prediction.strip())
    if date_from is not None:
        query = query.filter(Prediction.created_at >= date_from)
    if date_to is not None:
        query = query.filter(Prediction.created_at <= date_to)

    records = query.order_by(Prediction.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "image_path": r.image_path,
            "prediction": r.prediction,
            "confidence": r.confidence,
            "created_at": r.created_at,
        }
        for r in records
    ]


@router.delete("/results/{id}")
def delete_result(id: int, db: Session = Depends(get_db)):
    record = db.query(Prediction).filter(Prediction.id == id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Result not found")

    db.delete(record)
    db.commit()
    return {"deleted": True, "id": id}
