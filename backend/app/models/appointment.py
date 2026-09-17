from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    specialty = Column(String, nullable=False, default="GP Review")
    scheduled_time = Column(DateTime, nullable=False)
    status = Column(String, nullable=False, default="scheduled")  # scheduled | completed | cancelled | no_show
    no_show_risk = Column(Float, nullable=False, default=0.0)  # 0.0-1.0, predicted at booking time
    reminder_sent = Column(Integer, nullable=False, default=0)  # 0/1 as a simple boolean flag
    outcome_recorded_at = Column(DateTime, nullable=True)  # when `status` was last updated to a final state
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient")
