import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.data_loader import load_data
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(
    page_title="Bivariate Analysis | Startup Success",
    page_icon="🔍",
    layout="wide",
)


df_full = load_data()
if df_full is None:
    st.error("Dataset not found at `data/processed/processed_startups_data.csv`.")
    st.stop()

st.markdown("""
<style>
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}

/* Filter expander panel */
[data-testid="stExpander"] details,
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    background-color: #111111 !important;
    border-color: #444444 !important;
}
[data-testid="stExpander"] summary,
[data-testid="stExpander"] summary span,
[data-testid="stExpander"] label,
[data-testid="stExpander"] p,
[data-testid="stExpander"] h1,
[data-testid="stExpander"] h2,
[data-testid="stExpander"] h3 {
    color: #e8e8e8 !important;
}

/* Multiselect / select inputs */
[data-testid="stExpander"] [data-baseweb="select"],
[data-testid="stExpander"] [data-baseweb="select"] > div {
    background-color: #1e1e1e !important;
    border-color: #444444 !important;
}
[data-testid="stExpander"] [data-baseweb="select"] input,
[data-testid="stExpander"] [data-baseweb="select"] span,
[data-testid="stExpander"] [data-baseweb="select"] div {
    color: #e8e8e8 !important;
}
[data-testid="stExpander"] span[data-baseweb="tag"] {
    background-color: #333333 !important;
    color: #e8e8e8 !important;
    border-color: #555555 !important;
}

/* Dropdown menu */
div[data-baseweb="popover"] {
    background-color: #1e1e1e !important;
}
div[data-baseweb="popover"] li {
    color: #e8e8e8 !important;
    background-color: #1e1e1e !important;
}
div[data-baseweb="popover"] li:hover {
    background-color: #333333 !important;
}

/* Dark sidebar */
[data-testid="stSidebar"] {background-color:#111111 !important; color:#e8e8e8 !important;}
[data-testid="stSidebar"] .stSelectbox, [data-testid="stSidebar"] .stMultiSelect, [data-testid="stSidebar"] .stSlider, [data-testid="stSidebar"] .stRadio, [data-testid="stSidebar"] .stCheckbox {
    background-color:#111111 !important;
    color:#e8e8e8 !important;
    border-color:#444444 !important;
}
</style>
""", unsafe_allow_html=True)
# Ensure data types are consistent
df_full['founded_year'] = pd.to_numeric(df_full['founded_year'], errors='coerce')
df_full['funding_total_usd'] = pd.to_numeric(df_full['funding_total_usd'], errors='coerce')


STATUS_COLORS = {
    'operating': '#636EFA',
    'acquired':  '#00CC96',
    'ipo':       '#EF553B',
    'closed':    '#AB63FA',
}

# ── FILTER PANEL ─────────────────────────────────────────────────────────────
with st.expander("Filters", expanded=True):
    st.header("Filters")

    all_statuses = sorted(df_full['status'].dropna().unique().tolist())
    sel_status = st.multiselect(
        "Status",
        options=all_statuses,
        default=all_statuses,
    )

    top_countries = df_full['country_code'].value_counts().nlargest(30).index.tolist()
    sel_countries = st.multiselect(
        "Country (top 30)",
        options=top_countries,
        default=top_countries,
    )

    top_categories = df_full['category'].value_counts().nlargest(40).index.tolist()
    sel_categories = st.multiselect(
        "Industry (top 40)",
        options=top_categories,
        default=top_categories,
    )

    min_year = int(df_full['founded_year'].dropna().min())
    max_year = int(df_full['founded_year'].dropna().max())
    year_range = st.slider(
        "Year Founded",
        min_value=min_year, max_value=max_year,
        value=(1990, 2020),
    )

    max_rounds = int(df_full['funding_rounds'].max())
    rounds_range = st.slider(
        "Funding Rounds",
        min_value=0, max_value=max_rounds,
        value=(0, max_rounds),
    )

    fund_max = float(df_full['funding_total_usd'].max())
    fund_lo, fund_hi = st.slider(
        "Total Funding (USD)",
        min_value=0.0, max_value=fund_max,
        value=(0.0, fund_max),
    )

# ── APPLY FILTERS ────────────────────────────────────────────────────────────
df = df_full.copy()
if sel_status:
    df = df[df['status'].isin(sel_status)]
if sel_countries:
    df = df[df['country_code'].isin(sel_countries)]
if sel_categories:
    df = df[df['category'].isin(sel_categories)]
df = df[
    (df['founded_year'] >= year_range[0]) &
    (df['founded_year'] <= year_range[1])
]
df = df[df['funding_rounds'].between(rounds_range[0], rounds_range[1])]
df = df[df['funding_total_usd'].between(fund_lo, fund_hi) | df['funding_total_usd'].isna()]

st.header("2. Bivariate Analysis: What Drives Success?")
st.caption(f"{len(df):,} startups match current filters (of {len(df_full):,} total)")

if df.empty:
    st.warning("No data matches the current filters. Adjust the sidebar filters.")
    st.stop()

# ── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Funding vs. Status",
    "Location Analysis",
    "Time Trends",
    "Survival Rates",
    "Speed to Funding",
    "Life Span",
    "Lifespan vs Funding",
])

# ── TAB 1: FUNDING & STATUS ──────────────────────────────────────────────────
with tab1:
    st.subheader("Does More Money Mean Success?")
    fig = px.box(
        df, x='status', y='funding_total_usd',
        points="outliers", log_y=True,
        title='Funding Total by Startup Status',
        color='status',
        labels={'funding_total_usd': 'Total Funding (USD)', 'status': 'Status'},
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8', showlegend=True,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Insight:** Compare the median funding of 'acquired' startups versus 'closed' ones.")

# ── TAB 2: LOCATION ANALYSIS ─────────────────────────────────────────────────
with tab2:
    st.subheader("Startup Hubs: Top Countries")

    n_countries = st.slider("Number of countries to show", 5, 30, 10, key="loc_n")
    bar_mode = st.radio("Bar mode", ["group", "stack"], horizontal=True, key="loc_bar")

    top_c = df['country_code'].value_counts().nlargest(n_countries).index
    df_top = df[df['country_code'].isin(top_c)]

    fig = px.histogram(
        df_top, x='country_code', color='status',
        barmode=bar_mode,
        title=f'Status Distribution in Top {n_countries} Countries',
        labels={'country_code': 'Country Code', 'count': 'Number of Startups'},
        color_discrete_map=STATUS_COLORS,
        category_orders={'country_code': df_top['country_code'].value_counts().index.tolist()},
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8',
    )
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 3: TIME TRENDS ───────────────────────────────────────────────────────
with tab3:
    st.subheader("Funding Trends Over Time")

    metric = st.radio(
        "Metric", ["Mean", "Median", "Total"], horizontal=True, key="time_metric"
    )
    agg_fn = {'Mean': 'mean', 'Median': 'median', 'Total': 'sum'}[metric]

    funding_trend = (
        df.groupby('founded_year')['funding_total_usd']
        .agg(agg_fn)
        .reset_index()
    )
    funding_trend = funding_trend[
        (funding_trend['founded_year'] >= year_range[0]) &
        (funding_trend['founded_year'] <= year_range[1])
    ]

    fig = px.line(
        funding_trend, x='founded_year', y='funding_total_usd',
        title=f'{metric} Funding per Startup by Year Founded',
        markers=True,
        labels={'founded_year': 'Year Founded', 'funding_total_usd': f'{metric} Funding (USD)'},
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8',
    )
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 4: SURVIVAL RATES ────────────────────────────────────────────────────
with tab4:
    st.subheader("Which Industries Stay in the Market?")

    n_industries = st.slider("Number of industries to show", 10, 50, 30, key="surv_n")

    category_totals = df['category'].value_counts().reset_index()
    category_totals.columns = ['Category', 'Total_Startups']
    operating_counts = (
        df[df['status'] == 'operating']['category']
        .value_counts().reset_index()
    )
    operating_counts.columns = ['Category', 'Operating_Count']
    survival_df = pd.merge(category_totals, operating_counts, on='Category', how='left')
    survival_df['Operating_Count'] = survival_df['Operating_Count'].fillna(0)
    survival_df['Survival_Rate'] = (
        survival_df['Operating_Count'] / survival_df['Total_Startups']
    ) * 100
    top_n = survival_df.nlargest(n_industries, 'Total_Startups').sort_values('Survival_Rate', ascending=True)

    fig = px.bar(
        top_n, x='Survival_Rate', y='Category', orientation='h',
        title=f'Survival Rate: % of Startups Still Operating (Top {n_industries} Industries)',
        labels={'Survival_Rate': 'Survival Rate (%)', 'Category': 'Industry'},
        text='Survival_Rate',
        color='Survival_Rate',
        color_continuous_scale='Teal',
    )
    fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig.update_layout(
        xaxis_range=[0, 110],
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8', coloraxis_showscale=False,
        height=max(500, n_industries * 22),
    )
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 5: SPEED TO FUNDING ──────────────────────────────────────────────────
with tab5:
    st.subheader("How long does it take to get the first check?")

    df_timing = df[df['status'].isin(['operating', 'acquired', 'ipo', 'closed'])].copy()
    df_timing['days_to_first_funding'] = (
        df_timing['first_funding_at'] - df_timing['founded_at']
    ).dt.days
    df_timing = df_timing[df_timing['days_to_first_funding'] >= 0]

    show_pts = st.radio("Show points", ["outliers", "all", False], horizontal=True, key="spd_pts")

    fig = px.box(
        df_timing, x='status', y='days_to_first_funding',
        color='status',
        title='Time from Founding to First Funding (Days)',
        labels={'days_to_first_funding': 'Days to First Funding', 'status': 'Startup Status'},
        points=show_pts,
        color_discrete_map=STATUS_COLORS,
    )
    fig.update_layout(
        yaxis_type="log",
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8', showlegend=False,
    )
    fig.update_traces(marker=dict(size=3))
    st.plotly_chart(fig, use_container_width=True)

# ── TAB 6: LIFESPAN ──────────────────────────────────────────────────────────
with tab6:
    st.subheader("Lifecycle: Time Active in Market")

    df_life = df[df['lifespan_days'] > 0].copy()
    df_life['lifespan_years'] = df_life['lifespan_days'] / 365

    show_outliers = st.checkbox("Show Outliers", value=True, key="life_outliers")

    fig = px.box(
        df_life, x='status', y='lifespan_years',
        color='status',
        title='Distribution of Startup Lifespan (Years) by Status',
        labels={'lifespan_years': 'Time Active (Years)', 'status': 'Status'},
        color_discrete_map=STATUS_COLORS,
    )

    if show_outliers:
        fig.update_layout(yaxis_autorange=True)
    else:
        grouped = df_life.groupby('status')['lifespan_years']
        Q3 = grouped.quantile(0.75)
        IQR = Q3 - grouped.quantile(0.25)
        zoom_limit = (Q3 + 1.5 * IQR).max() + 1
        fig.update_layout(yaxis_type="linear", yaxis_range=[0, zoom_limit])

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8', showlegend=False,
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("**Insight:** Uncheck the box to zoom in on the typical lifecycle, hiding rare 50+ year companies.")

# ── TAB 7: LIFESPAN VS FUNDING (numpy trend lines — no statsmodels) ──────────
with tab7:
    st.subheader("Does surviving longer cost more money?")

    df_life = df[(df['lifespan_days'] > 0) & (df['funding_total_usd'] > 0)].copy()
    df_life['lifespan_years'] = df_life['lifespan_days'] / 365
    df_life['log_funding'] = np.log10(df_life['funding_total_usd'])

    show_trend = st.checkbox("Show trend lines (numpy OLS)", value=True, key="trend_lines")
    opacity = st.slider("Point opacity", 0.1, 1.0, 0.3, 0.05, key="scatter_opacity")

    fig = px.scatter(
        df_life,
        x='lifespan_years', y='funding_total_usd',
        color='status',
        log_y=True,
        title='Correlation: Time Active vs. Total Funding',
        labels={'lifespan_years': 'Years Active', 'funding_total_usd': 'Total Funding (USD)'},
        opacity=opacity,
        color_discrete_map=STATUS_COLORS,
        hover_name='name',
    )

    # Manual numpy linear trend lines on log(funding) vs lifespan_years
    if show_trend:
        for status, color in STATUS_COLORS.items():
            subset = df_life[df_life['status'] == status].dropna(subset=['lifespan_years', 'log_funding'])
            if len(subset) < 5:
                continue
            x = subset['lifespan_years'].values
            y = subset['log_funding'].values
            coeffs = np.polyfit(x, y, 1)
            x_line = np.linspace(x.min(), x.max(), 100)
            y_line = np.polyval(coeffs, x_line)
            fig.add_trace(go.Scatter(
                x=x_line,
                y=10 ** y_line,   # back to linear scale for log_y axis
                mode='lines',
                name=f'{status} trend',
                line=dict(color=color, width=2, dash='dash'),
                showlegend=True,
            ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color='#e8e8e8',
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Trend lines computed via numpy polyfit on log₁₀(funding) — no statsmodels required.")
