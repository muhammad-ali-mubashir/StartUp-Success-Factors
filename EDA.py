import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Startup Success Analysis",
    page_icon="🚀",
    layout="wide"
)

st.title("Startup Success Factors: Explanatory Data Analysis")
st.markdown("""
This dashboard visualizes key success factors for startups, including funding trends, 
geographical hubs, and survival rates across different industries.
""")

# -----------------------------------------------------------------------------
# 2. DATA LOADING & PREPROCESSING
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        # Load your dataset
        df = pd.read_csv('data/processed/processed_startups_data.csv')
        
        # Convert date columns to datetime objects for time-series analysis
        date_cols = ['founded_at', 'first_funding_at', 'last_funding_at']
        for col in date_cols:
            df[col] = pd.to_datetime(df[col], errors='coerce')
            
        # Extract 'Year Founded' for easier grouping
        df['founded_year'] = df['founded_at'].dt.year
        
        # Calculate 'Lifespan' (Time between founding and last funding/event)
        df['lifespan_days'] = (df['last_funding_at'] - df['founded_at']).dt.days
        
        return df
    except FileNotFoundError:
        return None

df = load_data()

if df is None:
    st.error("File 'processed_startups_data.csv' not found! Please place the file in the same directory as this script.")
    st.stop()

# Show raw data preview checkbox
if st.checkbox("Show Raw Data Preview"):
    st.dataframe(df.head())

# -----------------------------------------------------------------------------
# 3. UNIVARIATE ANALYSIS (Understanding Single Variables)
# -----------------------------------------------------------------------------
st.header("1. Univariate Analysis")
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution of Startup Status")
    status_counts = df['status'].value_counts().reset_index()
    status_counts.columns = ['Status', 'Count']
    fig_status = px.pie(status_counts, values='Count', names='Status', 
                        title='Startup Status Breakdown', hole=0.4)
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    st.subheader("Distribution of Funding Rounds")
    fig_rounds = px.histogram(
        df, 
        x='funding_rounds', 
        color='status', # Segmented by Status
        nbins=20, 
        title='Frequency of Funding Rounds (Segmented by Status)',
        labels={'funding_rounds': 'Number of Rounds', 'count': 'Number of Startups'},
        barmode='stack',
        color_discrete_sequence=px.colors.qualitative.G10
    )
    st.plotly_chart(fig_rounds, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 15 Startup Categories")
    top_cats = df['category'].value_counts().nlargest(15).reset_index()
    top_cats.columns = ['Category', 'Count']
    fig_cat = px.bar(top_cats, x='Count', y='Category', orientation='h',
                     title='Most Popular Industries', color='Count',
                     color_continuous_scale='Viridis')
    fig_cat.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_cat, use_container_width=True)

with col4:
    st.subheader("Total Funding Distribution (Log Scale)")
    fig_fund = px.histogram(df, x='funding_total_usd', log_y=True, nbins=50,
                            title='Funding Amount Distribution',
                            labels={'funding_total_usd': 'Total Funding (USD)'},
                            color_discrete_sequence=['#EF553B'])
    st.plotly_chart(fig_fund, use_container_width=True)

# -----------------------------------------------------------------------------
# 4. BIVARIATE ANALYSIS (Relationships & Success Factors)
# -----------------------------------------------------------------------------
st.header("2. Bivariate Analysis: What Drives Success?")

tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Funding vs. Status", 
    "Location Analysis", 
    "Time Trends", 
    "Survival Rates",
    "Speed to Funding",
    "Life Span",
    "lifespan vs Funding"
])

# --- TAB 1: FUNDING & STATUS ---
with tab1:
    st.subheader("Does More Money Mean Success?")
    fig_box = px.box(df, x='status', y='funding_total_usd', points="outliers",
                     log_y=True,
                     title='Funding Total by Startup Status',
                     color='status',
                     labels={'funding_total_usd': 'Total Funding (USD)', 'status': 'Status'})
    st.plotly_chart(fig_box, use_container_width=True)
    st.markdown("**Insight:** Compare the median funding of 'acquired' startups versus 'closed' ones.")

# --- TAB 2: LOCATION ANALYSIS ---
with tab2:
    st.subheader("Startup Hubs: Top Countries")
    top_countries_list = df['country_code'].value_counts().nlargest(10).index
    df_top_countries = df[df['country_code'].isin(top_countries_list)]
    
    fig_country = px.histogram(df_top_countries, x='country_code', color='status',
                               barmode='group',
                               title='Status Distribution in Top 10 Countries',
                               labels={'country_code': 'Country Code', 'count': 'Number of Startups'})
    st.plotly_chart(fig_country, use_container_width=True)

# --- TAB 3: TIME TRENDS ---
with tab3:
    st.subheader("Funding Trends Over Time")
    funding_trend = df.groupby('founded_year')['funding_total_usd'].mean().reset_index()
    funding_trend = funding_trend[(funding_trend['founded_year'] >= 1990) & (funding_trend['founded_year'] <= 2023)]
    
    fig_line = px.line(funding_trend, x='founded_year', y='funding_total_usd',
                       title='Average Funding per Startup by Year Founded',
                       markers=True,
                       labels={'founded_year': 'Year Founded', 'funding_total_usd': 'Avg Funding (USD)'})
    st.plotly_chart(fig_line, use_container_width=True)

# --- TAB 4: SURVIVAL RATES ---
with tab4:
    st.subheader("Which Industries Stay in the Market?")
    
    # Data Prep for Survival
    category_totals = df['category'].value_counts().reset_index()
    category_totals.columns = ['Category', 'Total_Startups']

    operating_counts = df[df['status'] == 'operating']['category'].value_counts().reset_index()
    operating_counts.columns = ['Category', 'Operating_Count']

    survival_df = pd.merge(category_totals, operating_counts, on='Category', how='left')
    survival_df['Operating_Count'] = survival_df['Operating_Count'].fillna(0)
    survival_df['Survival_Rate'] = (survival_df['Operating_Count'] / survival_df['Total_Startups']) * 100

    # Filter Top 30
    top_30_categories = survival_df.nlargest(30, 'Total_Startups')
    top_30_categories = top_30_categories.sort_values('Survival_Rate', ascending=True)

    fig_survival = px.bar(
        top_30_categories, 
        x='Survival_Rate', 
        y='Category', 
        orientation='h',
        title="Survival Rate: Percentage of Startups Still Operating (Top 30 Industries)",
        labels={'Survival_Rate': 'Survival Rate (%)', 'Category': 'Industry'},
        text='Survival_Rate',
        color='Survival_Rate', 
        color_continuous_scale='Teal'
    )
    fig_survival.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
    fig_survival.update_layout(xaxis_range=[0, 110])

    st.plotly_chart(fig_survival, use_container_width=True)

# --- TAB 5: SPEED TO FUNDING ---
with tab5:
    st.subheader("How long does it take to get the first check?")
    
    # Data Prep for Timing
    target_statuses = ['operating', 'acquired', 'ipo', 'closed']
    df_timing = df[df['status'].isin(target_statuses)].copy()
    df_timing['days_to_first_funding'] = (df_timing['first_funding_at'] - df_timing['founded_at']).dt.days
    df_timing = df_timing[df_timing['days_to_first_funding'] >= 0]

    fig_timing = px.box(
        df_timing, 
        x='status', 
        y='days_to_first_funding',
        color='status',
        title="Time from Founding to First Funding (Days)",
        labels={'days_to_first_funding': 'Days to First Funding', 'status': 'Startup Status'},
        points="outliers", 
        color_discrete_map={'operating': '#636EFA', 'acquired': '#00CC96', 'ipo': '#AB63FA', 'closed': '#EF553B'}
    )
    fig_timing.update_layout(yaxis_type="log") 
    fig_timing.update_traces(marker=dict(size=3))

    st.plotly_chart(fig_timing, use_container_width=True)

# --- TAB 6: LIFESPAN ANALYSIS (New Addition) ---
# Add "Lifespan Analysis" to your st.tabs() list first:
# tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([... "Lifespan Analysis"])

with tab6:
    st.subheader("Lifecycle: Time Active in Market")
    
    # 1. Filter Data
    df_life = df[df['lifespan_days'] > 0].copy()
    df_life['lifespan_years'] = df_life['lifespan_days'] / 365

    # --- INTERACTIVE CONTROL ---
    show_outliers = st.checkbox("Show Outliers", value=True)

    # 2. Visualization: Box Plot
    fig_lifespan = px.box(
        df_life,
        x='status',
        y='lifespan_years',
        color='status',
        title='Distribution of Startup Lifespan (Years) by Status',
        labels={'lifespan_years': 'Time Active (Years)', 'status': 'Status'},
        # Hide dots if unchecked
        # points="outliers" if show_outliers else False,
        color_discrete_map={
            'operating': '#636EFA', 
            'acquired': '#00CC96', 
            'ipo': '#AB63FA', 
            'closed': '#EF553B'
        }
    )

    # --- SMART SCALE LOGIC ---
    if show_outliers:
        # Full view with Log Scale to accommodate extreme outliers
        fig_lifespan.update_layout(yaxis_autorange=True)
    else:
        # ZOOMED VIEW: Find the "highest" upper fence among all categories
        # This ensures we don't cut off the whisker of the tallest box (e.g. IPO)
        
        # 1. Group by status to calculate stats per category
        grouped = df_life.groupby('status')['lifespan_years']
        Q1 = grouped.quantile(0.25)
        Q3 = grouped.quantile(0.75)
        IQR = Q3 - Q1
        
        # 2. Calculate the upper whisker limit for each status
        upper_fences = Q3 + (1.5 * IQR)
        
        # 3. Find the maximum of these limits
        max_limit = upper_fences.max()
        
        # 4. Set the view to fit the tallest whisker + buffer
        zoom_limit = max_limit + 1 

        fig_lifespan.update_layout(
            yaxis_type="linear", 
            yaxis_range=[0, zoom_limit],
            
        )

    st.plotly_chart(fig_lifespan, use_container_width=True)

    st.markdown("""
    **Insight:** Uncheck the box to zoom in on the "typical" lifecycle. This hides the rare 50+ year old companies and focuses on the standard 0-15 year range where most startups operate.
    """)
    
with tab7:
    st.subheader("Does surviving longer cost more money?")

    fig_money_time = px.scatter(
        df_life,
        x='lifespan_years',
        y='funding_total_usd',
        color='status',
        size='funding_rounds',
        log_y=True, # Funding is exponential
        title='Correlation: Time Active vs. Total Funding (with Trend Lines)',
        labels={'lifespan_years': 'Years Active', 'funding_total_usd': 'Total Funding (USD)'},
        opacity=0.3, # Make dots more transparent so lines pop out
        trendline="ols", # <--- Adds the Linear Trend Line
        # trendline="lowess" # <--- Alternative: Use 'lowess' for a curved smooth line (slower)
        color_discrete_map={
            'operating': '#636EFA', 
            'acquired': '#00CC96', 
            'ipo': '#AB63FA', 
            'closed': '#EF553B'
        }
    )

    st.plotly_chart(fig_money_time, use_container_width=True)
    st.caption("**Note:** Trend lines require the `statsmodels` library. If lines don't appear, run `pip install statsmodels`.")

# -----------------------------------------------------------------------------
# 5. MULTIVARIATE ANALYSIS (Complex Relationships)
# -----------------------------------------------------------------------------
st.header("3. Multivariate Analysis")
st.markdown("Explore complex relationships between 3+ variables.")

multi_tab1, multi_tab2, multi_tab3, multi_tab4 = st.tabs(["Investment Map", "Capital Hierarchy", "Trajectories", "Funding"])

# --- MULTI TAB 1: HEATMAP (Country vs Industry) ---
with multi_tab1:
    st.subheader("Innovation Hotspots: Country vs. Industry")
    
    # 1. Filter Data
    top_countries = df['country_code'].value_counts().nlargest(10).index
    top_categories = df['category'].value_counts().nlargest(10).index

    df_heatmap = df[
        (df['country_code'].isin(top_countries)) & 
        (df['category'].isin(top_categories))
    ]

    # 2. Dynamic Color Scaling (The Fix)
    # We calculate the counts first to find a good cutoff point
    counts = df_heatmap.groupby(['country_code', 'category']).size()
    
    # We set the max color to the 95th percentile. 
    # Any value above this (like the US) will just be the "Max" color.
    # This prevents one huge number from washing out the whole chart.
    z_max = counts.quantile(0.95)

    # 3. Create Heatmap with range_color
    fig_heatmap = px.density_heatmap(
        df_heatmap, 
        x='country_code', 
        y='category', 
        z='name', 
        histfunc='count',
        title='Concentration of Startups (Color Scale Capped at 95th Percentile)',
        labels={'country_code': 'Country', 'category': 'Industry', 'name': 'Count'},
        color_continuous_scale='Viridis',
        range_color=[0, z_max] # <--- This applies the cap
    )
    
    st.plotly_chart(fig_heatmap, use_container_width=True)
    st.caption(f"**Note:** The color scale is capped at {int(z_max)} to make smaller industries visible. The US value is likely much higher than this cap.")

# --- MULTI TAB 2: SUNBURST (Money Flow) ---
with multi_tab2:
    st.subheader("Where does the money live?")
    
    top_15_cats = df['category'].value_counts().nlargest(15).index
    df_sunburst = df[df['category'].isin(top_15_cats)]

    fig_sun = px.sunburst(
        df_sunburst, 
        path=['category', 'status'], 
        values='funding_total_usd',
        title='Total Capital Raised by Category and Status',
        color='funding_total_usd',
        color_continuous_scale='RdBu',
    )
    st.plotly_chart(fig_sun, use_container_width=True)

# --- MULTI TAB 3: FACETED SCATTER (Trajectories) ---
with multi_tab3:
    st.subheader("Funding Trajectories by Industry")
    
    target_industries = ['Technology', 'Health & Biotechnology', 'E-Commerce & Retail', 'Media & Entertainment']
    df_facet = df[df['category'].isin(target_industries)]

    fig_facet = px.scatter(
        df_facet, 
        x='funding_rounds', 
        y='funding_total_usd', 
        color='status', 
        facet_col='category', 
        facet_col_wrap=2, # Wrap to 2 columns for better layout
        log_y=True,
        title='Funding vs. Rounds: Industry Comparison',
        labels={'funding_rounds': 'Rounds', 'funding_total_usd': 'Funding (USD)'},
        height=600
    )
    st.plotly_chart(fig_facet, use_container_width=True)

with multi_tab4: 
    st.subheader("Funding Rounds vs. Total Funding vs. Status")

    fig_scatter = px.scatter(df, x='funding_rounds', y='funding_total_usd',
                            color='status',
                            size='funding_rounds',
                            hover_name='name',
                            log_y=True,
                            title='Relationship: Rounds, Funding Amount, and Status',
                            labels={'funding_rounds': 'Funding Rounds', 'funding_total_usd': 'Total Funding (USD)'},
                            opacity=0.6,
                            color_discrete_map={
                                'operating': '#636EFA', 
                                'acquired': '#00CC96', 
                                'ipo': '#AB63FA', 
                                'closed': '#EF553B'
                            })

    st.plotly_chart(fig_scatter, use_container_width=True)

st.success("Dashboard Analysis Complete!")