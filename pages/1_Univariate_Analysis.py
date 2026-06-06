import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_data
import plotly.express as px

st.set_page_config(
    page_title="Univariate Analysis | Startup Success",
    page_icon="📊",
    layout="wide",
)

st.markdown("""
<style>
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

df = load_data()
if df is None:
    st.error("Dataset not found at `data/processed/processed_startups_data.csv`.")
    st.stop()

st.title("Startup Success Factors: Explanatory Data Analysis")
st.markdown("This dashboard visualizes key success factors for startups, including funding trends, geographical hubs, and survival rates across different industries.")

if st.checkbox("Show Raw Data Preview"):
    st.dataframe(df.head(), use_container_width=True)

# ── 1. UNIVARIATE ANALYSIS ──────────────────────────────────────────────────
st.header("1. Univariate Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution of Startup Status")
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig = px.pie(
        status_counts, values='Count', names='Status',
        title='Startup Status Breakdown', hole=0.4,
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8e8e8')
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Distribution of Funding Rounds")
    fig = px.histogram(
        df, x='funding_rounds', color='status', nbins=20,
        title='Frequency of Funding Rounds (Segmented by Status)',
        labels={'funding_rounds': 'Number of Rounds', 'count': 'Number of Startups'},
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.G10,
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8e8e8')
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 15 Startup Categories")
    top_cats = df['category'].value_counts().nlargest(15).reset_index()
    top_cats.columns = ['Category', 'Count']
    fig = px.bar(
        top_cats, x='Count', y='Category', orientation='h',
        title='Most Popular Industries', color='Count',
        color_continuous_scale='Blues',
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8', coloraxis_showscale=False,
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Total Funding Distribution (Log Scale)")
    fig = px.histogram(
        df, x='funding_total_usd', log_y=True, nbins=50,
        title='Funding Amount Distribution',
        labels={'funding_total_usd': 'Total Funding (USD)'},
        color_discrete_sequence=['#EF553B'],
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e8e8e8')
    st.plotly_chart(fig, use_container_width=True)
