from datetime import datetime, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.appointment import Appointment
from app.models.patient import Patient

router = APIRouter()


class AppointmentCreate(BaseModel):
    patient_name: str
    specialty: str = "GP Review"
    scheduled_time: datetime


class OutcomeUpdate(BaseModel):
    status: Literal["completed", "no_show", "cancelled"]


def _estimate_no_show_risk(specialty: str, scheduled_time: datetime) -> float:
    """
    Simple, explainable heuristic (not an ML model): risk goes up for
    early-morning slots and for specialties that historically see more
    no-shows, and down for slots booked well in advance.
    """
    risk = 0.15

    if scheduled_time.hour < 9:
        risk += 0.15

    if specialty.lower() in ("follow-up", "gp review"):
        risk += 0.10

    days_out = (scheduled_time - datetime.utcnow()).days
    if days_out > 7:
        risk += 0.10
    elif days_out < 1:
        risk -= 0.05

    return round(max(0.05, min(risk, 0.95)), 2)


@router.get("/appointments")
def list_appointments(db: Session = Depends(get_db)):
    appointments = (
        db.query(Appointment)
        .order_by(Appointment.scheduled_time.asc())
        .all()
    )
    return [
        {
            "id": a.id,
            "patient_name": a.patient.name if a.patient else "Unknown",
            "specialty": a.specialty,
            "scheduled_time": a.scheduled_time.isoformat(),
            "status": a.status,
            "no_show_risk": a.no_show_risk,
            "reminder_sent": bool(a.reminder_sent),
        }
        for a in appointments
    ]


@router.post("/appointments")
def create_appointment(req: AppointmentCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.name == req.patient_name).first()
    if not patient:
        patient = Patient(name=req.patient_name)
        db.add(patient)
        db.flush()  # assigns patient.id before we use it below

    risk = _estimate_no_show_risk(req.specialty, req.scheduled_time)

    appointment = Appointment(
        patient_id=patient.id,
        specialty=req.specialty,
        scheduled_time=req.scheduled_time,
        no_show_risk=risk,
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return {"id": appointment.id, "no_show_risk": risk}


@router.get("/best-slot")
def best_slot(specialty: str = "GP Review", db: Session = Depends(get_db)):
    """
    Suggest the lowest-no-show-risk slot among the next 5 weekdays,
    working 1pm-3pm, avoiding times already booked for that specialty.
    """
    booked_times = {
        a.scheduled_time.replace(second=0, microsecond=0)
        for a in db.query(Appointment).filter(Appointment.specialty == specialty).all()
    }

    candidates = []
    day = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
    days_checked = 0
    while days_checked < 5:
        day += timedelta(days=1)
        if day.weekday() >= 5:  # skip weekends
            continue
        days_checked += 1
        for hour in (13, 14, 15):
            slot = day.replace(hour=hour)
            if slot in booked_times:
                continue
            candidates.append(slot)

    if not candidates:
        raise HTTPException(status_code=404, detail="No available slots found")

    best = min(candidates, key=lambda s: _estimate_no_show_risk(specialty, s))
    return {
        "slot": best.isoformat(),
        "estimated_no_show_risk": _estimate_no_show_risk(specialty, best),
    }


@router.post("/appointments/{appointment_id}/remind")
def send_reminder(appointment_id: int, db: Session = Depends(get_db)):
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    # No real SMS/email integration here — this just records that a reminder
    # was sent, which is enough to drive the frontend's confirmation state.
    appointment.reminder_sent = 1
    db.commit()
    return {"id": appointment.id, "reminder_sent": True}


@router.patch("/appointments/{appointment_id}/outcome")
def record_outcome(appointment_id: int, req: OutcomeUpdate, db: Session = Depends(get_db)):
    """
    Record what actually happened for a past appointment (completed / no_show /
    cancelled). This is what makes no-show *prediction* checkable against
    reality, rather than a number nobody ever verifies.
    """
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")

    appointment.status = req.status
    appointment.outcome_recorded_at = datetime.utcnow()
    db.commit()
    return {"id": appointment.id, "status": appointment.status}
