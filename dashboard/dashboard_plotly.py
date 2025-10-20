import plotly.express as px

def plot_budget(df):
    df['total_budget_final'] = df['total_budget'].fillna(df['computed_total'])
    fig = px.bar(df, x='sl_no', y='total_budget_final', hover_data=['description','qty'], color='needs_review', title='Budget by Item')
    return fig
