#!/bin/bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python deploy/init_db.py
python etl/etl_runner.py data/uploads/sample_budget.csv
streamlit run streamlit_app.py
