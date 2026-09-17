from collections import Counter, defaultdict
import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.hospital import Hospital
from app.models.triage_session import TriageSession

router = APIRouter()


@router.get("/hospitals")
def list_hospitals(db: Session = Depends(get_db)):
    """Full hospital capacity table, for the Dashboard page."""
    hospitals = db.query(Hospital).order_by(Hospital.capacity_pct.desc()).all()
    return [
        {"name": h.name, "capacity": h.capacity_pct, "status": h.status}
        for h in hospitals
    ]


@router.get("/hospitals/summary")
def hospitals_summary(db: Session = Depends(get_db)):
    """KPI row: max/avg capacity and count of available hospitals."""
    hospitals = db.query(Hospital).all()
    if not hospitals:
        return {"max_capacity": 0, "avg_capacity": 0, "available_count": 0}

    capacities = [h.capacity_pct for h in hospitals]
    available = sum(1 for h in hospitals if h.status == "Available")

    return {
        "max_capacity": max(capacities),
        "avg_capacity": round(sum(capacities) / len(capacities)),
        "available_count": available,
    }


@router.get("/triage-distribution")
def triage_distribution(db: Session = Depends(get_db)):
    """Counts of LOW vs URGENT (vs unclassified) across logged triage sessions."""
    sessions = db.query(TriageSession).all()
    counts = Counter(s.triage_level or "UNKNOWN" for s in sessions)
    return {
        "urgent": counts.get("URGENT", 0),
        "low": counts.get("LOW", 0),
        "unknown": counts.get("UNKNOWN", 0),
        "total": len(sessions),
    }


@router.get("/audit-trail")
def audit_trail(limit: int = 20, db: Session = Depends(get_db)):
    """Recent triage sessions, most recent first — backs the Clinical Audit Trail view."""
    sessions = (
        db.query(TriageSession)
        .order_by(TriageSession.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": s.id,
            "query": s.query_text,
            "answer": s.answer_text,
            "triage_level": s.triage_level,
            "sources": (s.sources or "").split(",") if s.sources else [],
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sessions
    ]


@router.get("/guideline-confidence")
def guideline_confidence(db: Session = Depends(get_db)):
    """
    Average retrieval confidence and retrieval count per guideline source,
    aggregated from logged triage sessions.

    NOTE: 'confidence' here is a heuristic derived from vector-similarity
    distance (see rag_pipeline._distance_to_confidence) — not a calibrated
    clinical confidence score.
    """
    sessions = db.query(TriageSession).filter(TriageSession.source_confidences.isnot(None)).all()

    totals = defaultdict(float)
    counts = defaultdict(int)

    for s in sessions:
        try:
            confidences = json.loads(s.source_confidences)
        except (TypeError, json.JSONDecodeError):
            continue
        for source, confidence in confidences.items():
            totals[source] += confidence
            counts[source] += 1

    rows = [
        {
            "guideline": source,
            "avg_confidence": round(totals[source] / counts[source], 3),
            "retrievals": counts[source],
        }
        for source in totals
    ]
    rows.sort(key=lambda r: r["avg_confidence"], reverse=True)
    return rows
