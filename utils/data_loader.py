import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    """Load and preprocess the startup dataset. Cached for performance."""
    try:
        df = pd.read_csv('data/processed/processed_startups_data.csv')

        date_cols = ['founded_at', 'first_funding_at', 'last_funding_at']
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')

        df['founded_year'] = df['founded_at'].dt.year
        df['lifespan_days'] = (df['last_funding_at'] - df['founded_at']).dt.days
        df['lifespan_years'] = df['lifespan_days'] / 365

        return df
    except FileNotFoundError:
        return None
