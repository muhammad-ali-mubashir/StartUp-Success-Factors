import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))
from utils.data_loader import load_data

st.set_page_config(
    page_title="Venture Alpha Engine",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

df = load_data()

st.title("Venture Alpha Engine")
st.markdown("This dashboard visualizes key success factors for startups, including funding trends, geographical hubs, and survival rates across different industries.")

st.divider()

if df is None:
    st.error("Dataset not found at `data/processed/processed_startups_data.csv`.")
    st.stop()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Startups", f"{len(df):,}")
col2.metric("Operating", f"{(df['status']=='operating').sum():,}")
col3.metric("Acquired", f"{(df['status']=='acquired').sum():,}")
col4.metric("IPO", f"{(df['status']=='ipo').sum():,}")
col5.metric("Closed", f"{(df['status']=='closed').sum():,}")

st.divider()

st.markdown("""
**Navigate using the sidebar** to explore the 9 analytical modules:

- **Univariate Analysis** — Module 01 · Module 02
- **Bivariate Analysis** — Module 03 · 04 · 05 · 06 · 07 · 08
- **Multivariate Analysis** — Module 09
""")

if st.checkbox("Show Raw Data Preview"):
    st.dataframe(df.head(20), use_container_width=True)
