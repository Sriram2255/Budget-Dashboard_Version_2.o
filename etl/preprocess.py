import pandas as pd

def clean_numeric_column(series):
    return pd.to_numeric(series.replace({'#REF!': pd.NA, '#ERROR!': pd.NA}), errors='coerce')

def parse_file(path):
    if path.lower().endswith('.csv'):
        df = pd.read_csv(path)
    else:
        df = pd.read_excel(path)
    return df

def transform(df):
    # create cleaned columns
    for col in ['weight /KG','Total weight /Kg','unit rate in INR','Total Budget']:
        if col in df.columns:
            df[col + '_clean'] = clean_numeric_column(df[col].astype(str))
        else:
            df[col + '_clean'] = pd.NA

    df['computed_total'] = pd.to_numeric(df.get('Qty', pd.Series([pd.NA]*len(df))), errors='coerce') * df['unit rate in INR_clean']
    df['needs_review'] = df[['weight /KG_clean','unit rate in INR_clean','Total Budget_clean']].isna().any(axis=1)

    df = df.rename(columns={
        'SL.NO':'sl_no',
        'DESCRIPTION':'description',
        'Responsible Agency':'responsible_agency',
        'Qty':'qty',
        'Duration':'duration_text',
        'weight /KG_clean':'weight_kg',
        'Total weight /Kg_clean':'total_weight_kg',
        'unit rate in INR_clean':'unit_rate_inr',
        'Total Budget_clean':'total_budget'
    })

    out_cols = ['sl_no','description','responsible_agency','qty','duration_text','weight_kg','total_weight_kg','unit_rate_inr','total_budget','computed_total','needs_review']
    for c in out_cols:
        if c not in df.columns:
            df[c] = pd.NA
    return df[out_cols]
