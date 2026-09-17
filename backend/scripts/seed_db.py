"""
Seed the database with realistic starter data so the Dashboard/Appointments/
Analytics pages have something real to show on first run.

Run from the `backend/` directory:
    python -m scripts.seed_db
"""
import os
import random
import sys
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal, init_db
from app.models.hospital import Hospital
from app.models.patient import Patient
from app.models.appointment import Appointment

HOSPITALS = [
    "University Hospital Southampton NHS FT",
    "Portsmouth Hospitals University NHS FT",
    "Hampshire Hospitals NHS FT",
    "Oxford University Hospitals NHS FT",
    "Royal Berkshire NHS FT",
    "Guy's and St Thomas' NHS FT",
    "King's College Hospital NHS FT",
    "St George's University Hospitals NHS FT",
    "Chelsea and Westminster Hospital NHS FT",
    "Imperial College Healthcare NHS Trust",
    "Barts Health NHS Trust",
    "Cambridge University Hospitals NHS FT",
    "Norfolk and Norwich University Hospitals NHS FT",
    "Leeds Teaching Hospitals NHS Trust",
    "Manchester University NHS FT",
]

PATIENT_NAMES = [
    "W. Werhclor", "J. Smith", "A. Patel", "M. Johnson", "S. Ahmed",
    "L. Brown", "R. Davies", "K. Wilson", "T. Evans", "N. Khan",
]

SPECIALTIES = ["Cardiology", "GP Review", "Follow-up", "Respiratory", "General Medicine"]


def seed():
    init_db()
    db = SessionLocal()
    random.seed(42)

    try:
        if db.query(Hospital).count() == 0:
            for name in HOSPITALS:
                db.add(Hospital(name=name, capacity_pct=random.randint(45, 99)))
            print(f"Seeded {len(HOSPITALS)} hospitals")

        if db.query(Patient).count() == 0:
            patients = [Patient(name=name, age=random.randint(18, 85)) for name in PATIENT_NAMES]
            db.add_all(patients)
            db.flush()  # get IDs before using them below
            print(f"Seeded {len(patients)} patients")
        else:
            patients = db.query(Patient).all()

        if db.query(Appointment).count() == 0:
            now = datetime.utcnow()
            for i in range(10):
                patient = random.choice(patients)
                db.add(Appointment(
                    patient_id=patient.id,
                    specialty=random.choice(SPECIALTIES),
                    scheduled_time=now + timedelta(days=random.randint(0, 5), hours=random.randint(8, 17)),
                    no_show_risk=round(random.uniform(0.05, 0.85), 2),
                ))
            print("Seeded 10 appointments")

        db.commit()
        print("Seed complete.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
