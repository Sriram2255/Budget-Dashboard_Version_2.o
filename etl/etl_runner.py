import argparse, os
import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from etl.preprocess import parse_file, transform
from etl.validator import validate_columns
from etl.summarizer_llm import summarize_change
import pandas as pd
from db.db_operations import replace_budget_items
from datetime import datetime, timezone  # Modified import

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to csv or excel file')
    parser.add_argument('--db', default=None, help='DB URL (optional)')
    args = parser.parse_args()

    path = args.path
    if not os.path.exists(path):
        raise SystemExit('File not found: ' + path)

    df = parse_file(path)
    missing = validate_columns(df)
    if missing:
        print('Missing columns:', missing)

    df_t = transform(df)
    df_t['created_at'] = datetime.now(timezone.utc)  # Modified line

    # Persist
    count = replace_budget_items(df_t, os.path.basename(path))
    print(f'Persisted {count} rows.')

    # Summarize & notify
    summary = summarize_change(df_t)
    print(summary)

def process_file(file_path):
    """Process uploaded file and load into database"""
    # Read file based on extension
    if file_path.endswith('.csv'):
        df = pd.read_csv(file_path)
    else:
        df = pd.read_excel(file_path)
    
    # Basic data cleaning
    df = df.fillna('')
    
    # Add metadata
    df['created_at'] = datetime.datetime.now()
    df['needs_review'] = False
    
    # Load into database
    replace_budget_items(df, os.path.basename(file_path))
    
    return True

if __name__ == '__main__':
    main()
