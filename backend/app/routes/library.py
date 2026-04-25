import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.library_item import LibraryItem

router = APIRouter(prefix="/api/v1", tags=["library"])


class LibraryItemInput(BaseModel):
    id: str
    name: str
    name_ar: str
    short: str
    short_ar: str
    symptoms_ar: list[str]
    red_flags_ar: list[str]
    safe_tips_ar: list[str]
    when_to_see_doctor_ar: str
    risk_level: str

    @field_validator("id", "name", "name_ar", "short", "short_ar", "when_to_see_doctor_ar", "risk_level")
    @classmethod
    def validate_required_text(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("Field is required")
        return text

    @field_validator("symptoms_ar", "red_flags_ar", "safe_tips_ar")
    @classmethod
    def validate_list_fields(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item.strip()]
        if not cleaned:
            raise ValueError("List must contain at least one non-empty item")
        return cleaned


@router.get("/library")
def list_library_items(
    q: str | None = Query(default=None),
    risk_level: str | None = Query(default=None),
    name: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(LibraryItem)
    if q and q.strip():
        term = f"%{q.strip()}%"
        query = query.filter((LibraryItem.name.ilike(term)) | (LibraryItem.name_ar.ilike(term)))
    if risk_level and risk_level.strip():
        query = query.filter(LibraryItem.risk_level == risk_level.strip())
    if name and name.strip():
        query = query.filter(LibraryItem.name == name.strip())

    rows = query.order_by(LibraryItem.name.asc()).all()
    return [
        {
            "id": row.disease_id,
            "name": row.name,
            "name_ar": row.name_ar,
            "short": row.short,
            "short_ar": row.short_ar,
            "symptoms_ar": json.loads(row.symptoms_ar),
            "red_flags_ar": json.loads(row.red_flags_ar),
            "safe_tips_ar": json.loads(row.safe_tips_ar),
            "when_to_see_doctor_ar": row.when_to_see_doctor_ar,
            "risk_level": row.risk_level,
        }
        for row in rows
    ]


@router.get("/library/{disease_id}")
def get_library_item(disease_id: str, db: Session = Depends(get_db)):
    row = db.query(LibraryItem).filter(LibraryItem.disease_id == disease_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Library item not found")
    return {
        "id": row.disease_id,
        "name": row.name,
        "name_ar": row.name_ar,
        "short": row.short,
        "short_ar": row.short_ar,
        "symptoms_ar": json.loads(row.symptoms_ar),
        "red_flags_ar": json.loads(row.red_flags_ar),
        "safe_tips_ar": json.loads(row.safe_tips_ar),
        "when_to_see_doctor_ar": row.when_to_see_doctor_ar,
        "risk_level": row.risk_level,
    }


@router.post("/library", status_code=status.HTTP_201_CREATED)
def create_library_item(payload: LibraryItemInput, db: Session = Depends(get_db)):
    exists = db.query(LibraryItem).filter(LibraryItem.disease_id == payload.id).first()
    if exists:
        raise HTTPException(status_code=400, detail="Library item id already exists")

    row = LibraryItem(
        disease_id=payload.id,
        name=payload.name,
        name_ar=payload.name_ar,
        short=payload.short,
        short_ar=payload.short_ar,
        symptoms_ar=json.dumps(payload.symptoms_ar),
        red_flags_ar=json.dumps(payload.red_flags_ar),
        safe_tips_ar=json.dumps(payload.safe_tips_ar),
        when_to_see_doctor_ar=payload.when_to_see_doctor_ar,
        risk_level=payload.risk_level,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.disease_id,
        "name": row.name,
        "name_ar": row.name_ar,
        "short": row.short,
        "short_ar": row.short_ar,
        "symptoms_ar": json.loads(row.symptoms_ar),
        "red_flags_ar": json.loads(row.red_flags_ar),
        "safe_tips_ar": json.loads(row.safe_tips_ar),
        "when_to_see_doctor_ar": row.when_to_see_doctor_ar,
        "risk_level": row.risk_level,
    }


@router.put("/library/{disease_id}")
def update_library_item(disease_id: str, payload: LibraryItemInput, db: Session = Depends(get_db)):
    row = db.query(LibraryItem).filter(LibraryItem.disease_id == disease_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Library item not found")

    # Allow updating identifier while preserving uniqueness.
    if payload.id != disease_id:
        collision = db.query(LibraryItem).filter(LibraryItem.disease_id == payload.id).first()
        if collision:
            raise HTTPException(status_code=400, detail="Target library item id already exists")
        row.disease_id = payload.id

    row.name = payload.name
    row.name_ar = payload.name_ar
    row.short = payload.short
    row.short_ar = payload.short_ar
    row.symptoms_ar = json.dumps(payload.symptoms_ar)
    row.red_flags_ar = json.dumps(payload.red_flags_ar)
    row.safe_tips_ar = json.dumps(payload.safe_tips_ar)
    row.when_to_see_doctor_ar = payload.when_to_see_doctor_ar
    row.risk_level = payload.risk_level
    db.commit()
    db.refresh(row)
    return {
        "id": row.disease_id,
        "name": row.name,
        "name_ar": row.name_ar,
        "short": row.short,
        "short_ar": row.short_ar,
        "symptoms_ar": json.loads(row.symptoms_ar),
        "red_flags_ar": json.loads(row.red_flags_ar),
        "safe_tips_ar": json.loads(row.safe_tips_ar),
        "when_to_see_doctor_ar": row.when_to_see_doctor_ar,
        "risk_level": row.risk_level,
    }


@router.delete("/library/{disease_id}")
def delete_library_item(disease_id: str, db: Session = Depends(get_db)):
    row = db.query(LibraryItem).filter(LibraryItem.disease_id == disease_id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Library item not found")

    db.delete(row)
    db.commit()
    return {"deleted": True, "id": disease_id}
