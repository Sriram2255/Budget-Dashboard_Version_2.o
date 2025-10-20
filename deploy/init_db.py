import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, Boolean, DateTime
from db.db_config import DB_URL
import datetime

def init_db():
    engine = create_engine(DB_URL, echo=True)
    metadata = MetaData()

    # Define the budget_items table
    budget_items = Table('budget_items', metadata,
        Column('id', Integer, primary_key=True),
        Column('project_id', Integer),
        Column('sl_no', Integer),
        Column('description', String),
        Column('responsible_agency', String),
        Column('qty', Float),
        Column('duration_text', String),
        Column('weight_kg', Float),
        Column('total_weight_kg', Float),
        Column('unit_rate_inr', Float),
        Column('total_budget', Float),
        Column('computed_total', Float),
        Column('needs_review', Boolean),
        Column('raw_file', String),
        Column('created_at', DateTime, default=datetime.datetime.utcnow)
    )

    # Create all tables
    metadata.create_all(engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
