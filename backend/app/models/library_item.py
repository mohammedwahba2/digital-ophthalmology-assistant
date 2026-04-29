from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.database.db import Base


class LibraryItem(Base):
    __tablename__ = "library_items"

    id = Column(Integer, primary_key=True, index=True)
    disease_id = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    name_ar = Column(String, nullable=False)
    short = Column(Text, nullable=False)
    short_ar = Column(Text, nullable=False)
    symptoms_ar = Column(Text, nullable=False)  # JSON array
    red_flags_ar = Column(Text, nullable=False)  # JSON array
    safe_tips_ar = Column(Text, nullable=False)  # JSON array
    when_to_see_doctor_ar = Column(Text, nullable=False)
    risk_level = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
