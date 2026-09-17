import json
import re

from sqlalchemy.orm import Session

from app.models.triage_session import TriageSession


def extract_triage_level(answer_text: str) -> str | None:
    """Pull 'LOW' or 'URGENT' out of the model's 'Triage Level: ...' line."""
    match = re.search(r"Triage Level:\s*(LOW|URGENT)", answer_text, re.IGNORECASE)
    return match.group(1).upper() if match else None


def log_triage_session(
    db: Session,
    query_text: str,
    answer_text: str,
    sources: list,
    source_confidences: dict | None = None,
) -> None:
    session = TriageSession(
        query_text=query_text,
        answer_text=answer_text,
        triage_level=extract_triage_level(answer_text),
        sources=",".join(sources) if sources else None,
        source_confidences=json.dumps(source_confidences) if source_confidences else None,
    )
    db.add(session)
    db.commit()
