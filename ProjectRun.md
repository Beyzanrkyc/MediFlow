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
