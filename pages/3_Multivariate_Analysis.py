import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_data
import plotly.express as px

st.set_page_config(
    page_title="Multivariate Analysis | Startup Success",
    page_icon="🌐",
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

STATUS_COLORS = {
    'operating': '#636EFA',
    'acquired':  '#00CC96',
    'ipo':       '#EF553B',
    'closed':    '#AB63FA',
}

st.header("3. Multivariate Analysis")
st.markdown("Explore complex relationships between 3+ variables.")

tab1, tab2, tab3, tab4 = st.tabs(["Investment Map", "Capital Hierarchy", "Trajectories", "Funding"])

# ── TAB 1: HEATMAP ──────────────────────────────────────────────────────────
with tab1:
    st.subheader("Innovation Hotspots: Country vs. Industry")
    top_countries = df['country_code'].value_counts().nlargest(10).index
    top_categories = df['category'].value_counts().nlargest(10).index
    df_heatmap = df[
        df['country_code'].isin(top_countries) &
        df['category'].isin(top_categories)
    ]
    counts = df_heatmap.groupby(['country_code', 'category']).size()
    z_max = counts.quantile(0.95)

    fig = px.density_heatmap(
        df_heatmap, x='country_code', y='category',
        z='name', histfunc='count',
        title='Concentration of Startups (Color Scale Capped at 95th Percentile)',
        labels={'country_code': 'Country', 'category': 'Industry', 'name': 'Count'},
        color_continuous_scale='Viridis',
        range_color=[0, z_max],
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8', height=500,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"**Note:** The color scale is capped at {int(z_max)} to make smaller industries visible.")

# ── TAB 2: SUNBURST ─────────────────────────────────────────────────────────
with tab2:
    st.subheader("Where does the money live?")
    top_15_cats = df['category'].value_counts().nlargest(15).index
    df_sunburst = df[df['category'].isin(top_15_cats)]

    fig = px.sunburst(
        df_sunburst,
        path=['category', 'status'],
        values='funding_total_usd',
        title='Total Capital Raised by Category and Status',
        color='funding_total_usd',
        color_continuous_scale='RdBu',
    )
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color='#e8e8e8', height=600)
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 3: FACETED SCATTER ──────────────────────────────────────────────────
with tab3:
    st.subheader("Funding Trajectories by Industry")
    target_industries = ['Technology', 'Health & Biotechnology', 'E-Commerce & Retail', 'Media & Entertainment']
    df_facet = df[df['category'].isin(target_industries)]

    if df_facet.empty:
        top4 = df['category'].value_counts().nlargest(4).index.tolist()
        df_facet = df[df['category'].isin(top4)]

    fig = px.scatter(
        df_facet,
        x='funding_rounds', y='funding_total_usd',
        color='status', facet_col='category',
        facet_col_wrap=2, log_y=True,
        title='Funding vs. Rounds: Industry Comparison',
        labels={'funding_rounds': 'Rounds', 'funding_total_usd': 'Funding (USD)'},
        height=600,
        color_discrete_map=STATUS_COLORS,
        opacity=0.55,
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8',
    )
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 4: SCATTER ──────────────────────────────────────────────────────────
with tab4:
    st.subheader("Funding Rounds vs. Total Funding vs. Status")
    fig = px.scatter(
        df,
        x='funding_rounds', y='funding_total_usd',
        color='status', size='funding_rounds',
        hover_name='name', log_y=True,
        title='Relationship: Rounds, Funding Amount, and Status',
        labels={'funding_rounds': 'Funding Rounds', 'funding_total_usd': 'Total Funding (USD)'},
        opacity=0.6,
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8', height=600,
    )
    st.plotly_chart(fig, use_container_width=True)

st.success("Dashboard Analysis Complete!")
