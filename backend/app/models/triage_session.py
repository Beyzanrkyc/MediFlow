from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db import Base


class TriageSession(Base):
    """One logged symptom-checker interaction, for the analytics/audit-trail views."""
    __tablename__ = "triage_sessions"

    id = Column(Integer, primary_key=True, index=True)
    query_text = Column(Text, nullable=False)
    answer_text = Column(Text, nullable=False)
    triage_level = Column(String, nullable=True)  # "LOW" | "URGENT" | None if undetermined
    sources = Column(Text, nullable=True)  # comma-separated source names
    source_confidences = Column(Text, nullable=True)  # JSON: {"source": confidence, ...}
    created_at = Column(DateTime, default=datetime.utcnow)
