# BHEL Budget Automation - Full Project

This project automates ingestion of budget Excel/CSV files, cleans and persists the records,
and provides an interactive Streamlit + Plotly dashboard. It supports recurrent automatic updates.

Folders:
- etl/: ETL scripts (preprocess, validator, runner)
- db/: DB init & operations
- dashboard/: modular dashboard components
- deploy/: init and helper scripts
- data/: uploads/ processed/ archive/

Default DB: PostgreSQL if DATABASE_URL is set, otherwise falls back to SQLite (budget.db).

LLM: A lightweight placeholder is included; if you set OPENAI_API_KEY, the summarizer will call OpenAI (optional).

Quickstart (local demo):
1. python -m venv .venv
2. source .venv/bin/activate
3. pip install -r requirements.txt
4. python deploy/init_db.py
5. python etl/etl_runner.py data/uploads/sample_budget.csv --db sqlite:///budget.db
6. streamlit run streamlit_app.py

