import os
import pandas as pd

def summarize_change(df):
    """Generate a summary of the budget data"""
    # Convert to numeric first to avoid warnings
    df['computed_total'] = pd.to_numeric(df['computed_total'], errors='coerce')
    df['total_budget'] = pd.to_numeric(df['total_budget'], errors='coerce')
    
    # Calculate totals
    total = df['computed_total'].fillna(0).sum() + df['total_budget'].fillna(0).sum()
    
    # Create summary without Unicode characters
    summary = f"""
Budget Summary:
--------------
Total Items: {len(df)}
Total Budget: INR {total:,.2f}
Items Needing Review: {df['needs_review'].sum()}
Agencies: {df['responsible_agency'].nunique()}
"""
    return summary
