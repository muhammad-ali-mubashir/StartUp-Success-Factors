# 🚀 Startup Success Factors — EDA Dashboard

A multi-page interactive Streamlit dashboard exploring the key factors that determine startup success, built on a Crunchbase-derived dataset of real-world ventures.

---

## 📐 App Structure — 9 Modules across 4 Pages

| Page | Modules | Theme |
|------|---------|-------|
| 🏠 **Home** | Overview + KPIs | Landing |
| 📊 **Univariate Analysis** | Module 01 · Module 02 | Single-variable exploration |
| 🔍 **Bivariate Analysis** | Module 03 · 04 · 05 · 06 · 07 · 08 | Two-variable relationships |
| 🌐 **Multivariate Analysis** | Module 09 | 3+ variable deep dives |

### The 9 Modules

| # | Module | Description |
|---|--------|-------------|
| 01 | Startup Overview & Distribution | Status pie chart + Top 15 industries |
| 02 | Funding Landscape | Funding rounds histogram + total capital distribution |
| 03 | Funding vs. Outcome | Does more money guarantee success? |
| 04 | Geographic Startup Hubs | Top-10 country comparison by startup status |
| 05 | Founding & Funding Time Trends | Average funding per cohort year (1990–2023) |
| 06 | Industry Survival Rates | % of startups still operating per sector |
| 07 | Speed to First Funding | Days from founding to first check by outcome |
| 08 | Startup Lifespan Analysis | Active duration + correlation with capital raised |
| 09 | Multivariate Deep Dive | Heatmap · Sunburst · Faceted scatter · Funding correlation |

---

## 📁 Project Structure

```
StartUp-Success-Factors/
├── Home.py                        # Entry point — landing page
├── pages/
│   ├── 1_Univariate_Analysis.py   # Modules 01–02
│   ├── 2_Bivariate_Analysis.py    # Modules 03–08
│   └── 3_Multivariate_Analysis.py # Module 09
├── utils/
│   ├── __init__.py
│   └── data_loader.py             # Shared cached data loading
├── data/
│   ├── raw/
│   │   └── big_startup_secsees_dataset.csv
│   └── processed/
│       └── processed_startups_data.csv
├── .streamlit/
│   └── config.toml                # Dark theme + server config
├── requirements.txt
└── README.md
```

---

## ⚙️ Local Setup

### 1. Clone the Repository
```bash
git clone https://github.com/muhammad-ali-mubashir/StartUp-Success-Factors.git
cd StartUp-Success-Factors
```

### 2. Create a Virtual Environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Ensure Data is in Place
The dashboard reads from:
```
data/processed/processed_startups_data.csv
```
If it's missing, run the preprocessing notebook (`data_preprocessing.ipynb`) first.

### 5. Run the App
```bash
streamlit run Home.py
```

The app will open at **http://localhost:8501**

---

## ☁️ Deploy to Streamlit Community Cloud

1. Push this repo to **GitHub** (ensure `data/processed/processed_startups_data.csv` is committed or accessible)
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New App**
3. Set:
   - **Repository:** `muhammad-ali-mubashir/StartUp-Success-Factors`
   - **Branch:** `main`
   - **Main file path:** `Home.py`
4. Click **Deploy** — Streamlit Cloud will install `requirements.txt` automatically.

> **Note on Data Size:** The processed CSV is ~6.5 MB. GitHub has a 100 MB limit for regular files, so this will deploy without issues. For larger datasets, use Git LFS or host on an external store (S3, GCS) and load via URL.

---

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| [Streamlit](https://streamlit.io) | Multi-page web app framework |
| [Pandas](https://pandas.pydata.org) | Data loading & transformation |
| [Plotly Express](https://plotly.com/python/plotly-express/) | Interactive visualizations |
| [Statsmodels](https://www.statsmodels.org) | OLS trend lines in scatter plots |

---

## 👥 Team

- **Ali** — Exploratory Data Analysis (`Ali_exploratory_data_analysis.ipynb`)
- **Saad** — Startup EDA (`Saad_startup_eda.ipynb`)
- **Tayyab** — Exploratory Analysis (`Tayyab_exploratory_analysis.ipynb`)
- **Dashboard** — Multi-page Streamlit app (`Home.py`, `pages/`)
