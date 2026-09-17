# Session changelog

Fixes and features added while debugging/extending the project:

## Fixed
- `backend/requirements.txt` was empty — reconstructed with pinned versions
  matching what was actually installed and working in the project's venv.
- `backend/app/routes/triage.py` — was returning a malformed nested response
  (`{"response": {...}}`) and took `query` as a raw URL param instead of a
  JSON body like `/api/chat` does. Fixed both.
- `backend/scripts/ingest_data.py` was incomplete — it extracted PDF text but
  never chunked/embedded/stored it, and was never actually invoked. Rewritten
  to run end-to-end, ingest local PDFs from `backend/data/nhs_guidelines/`,
  and cache any URL-downloaded PDFs locally. (The original hardcoded NICE
  URLs were also dead/incorrect — NICE resource URLs embed unpredictable
  numeric IDs, so local-file ingestion is now the primary path.)
- `.gitignore` was empty — `.env` was sitting untracked with nothing stopping
  it from being committed. Added a real `.gitignore`.

## Added — real PostgreSQL-backed data layer
Previously Dashboard/Appointments/Analytics were 100% hardcoded or
`np.random` data in Streamlit, with no backend calls at all except the
symptom checker chat.

- `backend/app/db.py` + SQLAlchemy models: `Patient`, `Appointment`,
  `Hospital`, `TriageSession`.
- `backend/scripts/seed_db.py` — seeds realistic starter data.
- `backend/app/routes/scheduling.py` — list/create appointments, a real
  best-slot suggestion heuristic, a no-show-risk heuristic, send-reminder.
- `backend/app/routes/analytics.py` — hospital capacity, KPI summary,
  triage-level distribution, audit trail, and a **real** guideline-confidence
  score derived from ChromaDB's actual similarity distances (previously
  hardcoded fake numbers).
- `chat.py` now logs every symptom-checker session (query, answer, triage
  level, retrieved sources + confidence) into `TriageSession`, so analytics
  and the audit trail have real data instead of being permanently empty.
- Rewired `frontend/pages/Dashboard.py`, `Analytics.py`, `Appointments.py`
  to call these endpoints instead of synthetic data. Anywhere a real data
  source doesn't exist yet (A&E patient-load curve, no-show *outcome*
  tracking), the UI says so explicitly rather than quietly faking it.

## Verified, not just written
All of the above was tested against a real local PostgreSQL instance and a
running FastAPI server (endpoints hit with curl), and the three rewired
Streamlit pages were executed via `streamlit.testing.v1.AppTest` against the
live backend, including clicking the "Remind" button and confirming the
state change persisted to the database. The RAG/LLM path (ChromaDB +
sentence-transformers + Groq) could not be fully re-tested in this sandbox
(no network access to Groq, and `torch` didn't fit the sandbox's disk quota)
— that part still needs verifying on your machine with a real `GROQ_API_KEY`.

## Still open
- README says the frontend is React/Next.js — it's actually Streamlit. Worth
  fixing before anyone reviews the repo.
- No-show *risk* is predicted but never checked against a real outcome —
  there's no field yet for "did they actually show up".
- The empty `Patient`/`Appointment`/`Hospital` model *files* referenced in
  the old README structure are now real (SQLAlchemy models); the route/model
  wiring is done, but there's no auth/patient-facing signup flow.

## To run locally
```bash
cd backend
pip install -r requirements.txt
# create a Postgres DB and set DATABASE_URL + GROQ_API_KEY in .env
python -m scripts.seed_db          # seed sample data
python -m scripts.ingest_data      # ingest NHS guideline PDFs (drop PDFs into backend/data/nhs_guidelines/ first)
uvicorn app.main:app --reload      # from inside backend/
# in another terminal, from the project root:
streamlit run app.py
```
