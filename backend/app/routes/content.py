import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.section import Section

router = APIRouter(prefix="/api/v1", tags=["content"])
ALLOWED_SECTION_TYPES = {"about", "safety", "education"}


class SectionInput(BaseModel):
    section_type: str
    title: str
    content: dict

    @field_validator("section_type")
    @classmethod
    def validate_section_type(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in ALLOWED_SECTION_TYPES:
            raise ValueError("section_type must be one of: about, safety, education")
        return normalized

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("title is required")
        return text


@router.get("/content")
def list_section_content(
    section_type: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(Section)
    if section_type:
        query = query.filter(Section.section_type == section_type.strip().lower())
    rows = query.order_by(Section.updated_at.desc()).all()
    return [
        {
            "id": row.id,
            "section_type": row.section_type,
            "title": row.title,
            "content": json.loads(row.content),
            "updated_at": row.updated_at,
        }
        for row in rows
    ]


@router.get("/content/{section_type}")
def get_section_content(section_type: str, db: Session = Depends(get_db)):
    normalized = section_type.strip().lower()
    if normalized not in ALLOWED_SECTION_TYPES:
        raise HTTPException(status_code=404, detail="Section not found")

    row = (
        db.query(Section)
        .filter(Section.section_type == normalized)
        .order_by(Section.updated_at.desc())
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="Section content not found")

    return {
        "id": row.id,
        "section_type": row.section_type,
        "title": row.title,
        "content": json.loads(row.content),
        "updated_at": row.updated_at,
    }


@router.post("/content", status_code=status.HTTP_201_CREATED)
def create_section_content(payload: SectionInput, db: Session = Depends(get_db)):
    row = Section(
        section_type=payload.section_type,
        title=payload.title,
        content=json.dumps(payload.content),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "section_type": row.section_type,
        "title": row.title,
        "content": json.loads(row.content),
        "updated_at": row.updated_at,
    }


@router.put("/content/{id}")
def update_section_content(id: int, payload: SectionInput, db: Session = Depends(get_db)):
    row = db.query(Section).filter(Section.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Section content not found")

    row.section_type = payload.section_type
    row.title = payload.title
    row.content = json.dumps(payload.content)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "section_type": row.section_type,
        "title": row.title,
        "content": json.loads(row.content),
        "updated_at": row.updated_at,
    }


@router.delete("/content/{id}")
def delete_section_content(id: int, db: Session = Depends(get_db)):
    row = db.query(Section).filter(Section.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Section content not found")

    db.delete(row)
    db.commit()
    return {"deleted": True, "id": id}
