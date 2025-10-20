from sqlalchemy import create_engine, text
import pandas as pd
from db.db_config import DB_URL

engine = create_engine(DB_URL, echo=False)

def read_budget_items():
    with engine.begin() as conn:
        return pd.read_sql('SELECT * FROM budget_items ORDER BY sl_no', conn)

def replace_budget_items(df, raw_file):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM budget_items WHERE project_id=1"))
        insert_stmt = text("""INSERT INTO budget_items
        (project_id, sl_no, description, responsible_agency, qty, duration_text,
        weight_kg, total_weight_kg, unit_rate_inr, total_budget, computed_total, needs_review, raw_file, created_at)
        VALUES
        (:project_id, :sl_no, :description, :responsible_agency, :qty, :duration_text,
         :weight_kg, :total_weight_kg, :unit_rate_inr, :total_budget, :computed_total, :needs_review, :raw_file, :created_at)
        """)
        rows = []
        for _, r in df.iterrows():
            # Handle NA values by converting them to None
            rows.append({
                'project_id': 1,
                'sl_no': int(r.sl_no) if pd.notna(r.sl_no) else None,
                'description': str(r.description) if pd.notna(r.description) else None,
                'responsible_agency': str(r.responsible_agency) if pd.notna(r.responsible_agency) else None,
                'qty': float(r.qty) if pd.notna(r.qty) else None,
                'duration_text': str(r.duration_text) if pd.notna(r.duration_text) else None,
                'weight_kg': float(r.weight_kg) if pd.notna(r.weight_kg) else None,
                'total_weight_kg': float(r.total_weight_kg) if pd.notna(r.total_weight_kg) else None,
                'unit_rate_inr': float(r.unit_rate_inr) if pd.notna(r.unit_rate_inr) else None,
                'total_budget': float(r.total_budget) if pd.notna(r.total_budget) else None,
                'computed_total': float(r.computed_total) if pd.notna(r.computed_total) else None,
                'needs_review': bool(r.needs_review),
                'raw_file': raw_file,
                'created_at': r.get('created_at').strftime('%Y-%m-%d %H:%M:%S') if pd.notna(r.get('created_at')) else None
            })
        conn.execute(insert_stmt, rows)
        return len(rows)
