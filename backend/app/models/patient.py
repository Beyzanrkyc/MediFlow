from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=True)
    contact = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
