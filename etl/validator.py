def validate_columns(df, required=['SL.NO','DESCRIPTION','Qty']):
    missing = [c for c in required if c not in df.columns]
    return missing
