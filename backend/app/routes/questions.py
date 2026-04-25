import json

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.models.question import Question

router = APIRouter(prefix="/api/v1", tags=["questions"])


class QuestionInput(BaseModel):
    question_text: str
    options: list[str]

    @field_validator("question_text")
    @classmethod
    def validate_question_text(cls, value: str) -> str:
        text = value.strip()
        if not text:
            raise ValueError("question_text is required")
        return text

    @field_validator("options")
    @classmethod
    def validate_options(cls, value: list[str]) -> list[str]:
        cleaned = [item.strip() for item in value if item.strip()]
        if len(cleaned) < 2:
            raise ValueError("At least 2 non-empty options are required")
        return cleaned


@router.get("/questions")
def list_questions(db: Session = Depends(get_db)):
    rows = db.query(Question).order_by(Question.created_at.desc()).all()
    return [
        {
            "id": row.id,
            "question_text": row.question_text,
            "options": json.loads(row.options),
            "created_at": row.created_at,
        }
        for row in rows
    ]


@router.post("/questions", status_code=status.HTTP_201_CREATED)
def create_question(payload: QuestionInput, db: Session = Depends(get_db)):
    row = Question(question_text=payload.question_text, options=json.dumps(payload.options))
    db.add(row)
    db.commit()
    db.refresh(row)
    return {
        "id": row.id,
        "question_text": row.question_text,
        "options": json.loads(row.options),
        "created_at": row.created_at,
    }


@router.put("/questions/{id}")
def update_question(id: int, payload: QuestionInput, db: Session = Depends(get_db)):
    row = db.query(Question).filter(Question.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Question not found")

    row.question_text = payload.question_text
    row.options = json.dumps(payload.options)
    db.commit()
    db.refresh(row)

    return {
        "id": row.id,
        "question_text": row.question_text,
        "options": json.loads(row.options),
        "created_at": row.created_at,
    }


@router.delete("/questions/{id}")
def delete_question(id: int, db: Session = Depends(get_db)):
    row = db.query(Question).filter(Question.id == id).first()
    if not row:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(row)
    db.commit()
    return {"deleted": True, "id": id}
