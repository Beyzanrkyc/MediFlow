from sqlalchemy import Column, Integer, String

from app.db import Base


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    capacity_pct = Column(Integer, nullable=False, default=0)  # 0-100

    @property
    def status(self) -> str:
        if self.capacity_pct > 90:
            return "Full"
        if self.capacity_pct > 75:
            return "Busy"
        return "Available"
