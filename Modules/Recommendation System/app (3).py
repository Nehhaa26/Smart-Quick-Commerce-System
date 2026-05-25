"""
app.py
──────
Smart Inventory Recommendation System — Streamlit UI

Prerequisites:
    1. Run train_model.py first to generate model.pkl
    2. Place app.py, train_model.py, model.pkl in the same folder

Run:
    streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import pickle
import datetime
import warnings
import pytz

warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Inventory Recommendation System",
    page_icon="📦",
    layout="centered",
)

# ─────────────────────────────────────────────────────────────
# DARK THEME — matches screenshot exactly
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* ── global background ── */
  .stApp, [data-testid="stAppViewContainer"],
  [data-testid="stHeader"], section[data-testid="stSidebar"] {
      background-color: #0e0e0e !important;
      color: #e0e0e0 !important;
  }
  .block-container { padding: 2rem 2rem 2rem 2rem; max-width: 860px; }

  /* ── title ── */
  .main-title {
      font-size: 2.1rem; font-weight: 800;
      color: #ffffff; margin-bottom: 0.2rem;
      display: flex; align-items: center; gap: 12px;
  }

  /* ── field labels ── */
  .field-label {
      font-size: 0.82rem; color: #a0a0b0;
      margin-bottom: 4px; margin-top: 16px;
  }

  /* ── selectbox / date input ── */
  [data-testid="stSelectbox"] > div > div,
  [data-testid="stDateInput"]  > div > div {
      background-color: #2a2a3e !important;
      border: 1px solid #3a3a5a !important;
      border-radius: 6px !important;
      color: #e0e0e0 !important;
  }
  [data-testid="stSelectbox"] svg { fill: #a0a0b0 !important; }

  /* ── info/warning banner ── */
  .info-banner {
      background: #3a3a10;
      border: 1px solid #6a6a20;
      border-radius: 6px;
      padding: 10px 16px;
      color: #d4d480;
      font-size: 0.85rem;
      margin: 16px 0 24px 0;
  }

  /* ── section header ── */
  .section-header {
      font-size: 1.25rem; font-weight: 700;
      color: #ffffff; margin: 28px 0 12px 0;
      display: flex; align-items: center; gap: 8px;
  }

  /* ── column headers ── */
  .col-header-high { font-size:1rem; font-weight:700; color:#ff6b35; margin-bottom:12px; }
  .col-header-med  { font-size:1rem; font-weight:700; color:#f0b429; margin-bottom:12px; }
  .col-header-low  { font-size:1rem; font-weight:700; color:#e05252; margin-bottom:12px; }

  /* ── category pills ── */
  .pill-high {
      background:#2a1f0a; border:1px solid #6a4a10;
      border-radius:6px; padding:12px 16px;
      color:#e0c060; font-size:0.9rem; margin-bottom:8px;
  }
  .pill-med {
      background:#2a2a0a; border:1px solid #5a5a10;
      border-radius:6px; padding:12px 16px;
      color:#c8c840; font-size:0.9rem; margin-bottom:8px;
  }
  .pill-low {
      background:#2a0a0a; border:1px solid #5a1010;
      border-radius:6px; padding:12px 16px;
      color:#c06060; font-size:0.9rem; margin-bottom:8px;
  }

  /* ── smart suggestions ── */
  .suggestions-title {
      font-size:1.1rem; font-weight:700;
      color:#f5c518; margin:28px 0 10px 0;
  }
  .suggestion-item {
      color:#c8c8d0; font-size:0.87rem;
      margin-bottom:6px; padding-left:4px;
  }
  .suggestion-item b { color:#ffffff; }

  /* ── model badge ── */
  .model-badge {
      background:#1a2a1a; border:1px solid #2a5a2a;
      border-radius:20px; padding:4px 14px;
      color:#6ab06a; font-size:0.78rem; display:inline-block;
      margin-top: 6px;
  }

  /* hide streamlit chrome */
  #MainMenu, footer, [data-testid="stToolbar"] { visibility:hidden; }
  div[data-testid="stDecoration"] { display:none; }
  [data-testid="stDeployButton"]  { visibility: visible !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# LOAD model.pkl
# ─────────────────────────────────────────────────────────────
MODEL_PATH = "model.pkl"

@st.cache_resource(show_spinner="Loading recommendation model…")
def load_model(path):
    with open(path, "rb") as f:
        return pickle.load(f)

try:
    bundle = load_model(MODEL_PATH)
except FileNotFoundError:
    st.error(
        "⚠️ `model.pkl` not found. "
        "Please run `python train_model.py` first to generate the model file."
    )
    st.stop()

# ─────────────────────────────────────────────────────────────
# LOAD context CSV for weather/season lookup on chosen date
# ─────────────────────────────────────────────────────────────
DATA_PATH = "QCFE9_Perfect_Discount_Statergy.csv"

@st.cache_data(show_spinner=False)
def load_context(path):
    df = pd.read_csv(
        path,
        usecols=["City", "Order_date", "Season", "Weather", "Peak_Intensity"],
    )
    df["Order_date"] = pd.to_datetime(df["Order_date"])
    return df

ctx_df = load_context(DATA_PATH)

# ─────────────────────────────────────────────────────────────
# CONSTANTS from bundle
# ─────────────────────────────────────────────────────────────
CITIES   = sorted(bundle["le_city"].classes_.tolist())
ALL_CATS = sorted(bundle["le_cat"].classes_.tolist())
agg      = bundle["agg"]

# ─────────────────────────────────────────────────────────────
# PREDICTION HELPERS
# ─────────────────────────────────────────────────────────────
def build_feature_row(city: str, chosen_date: datetime.date, category: str):
    """
    Build one feature row for the model.
    Uses historical city+category averages when exact date is not in dataset.
    Returns (feature_dict, exact_match_bool)
    """
    sub   = agg[(agg["City"] == city) & (agg["Product_Category"] == category)]
    exact = sub[sub["Order_date"].dt.date == chosen_date]

    if len(exact) > 0:
        row     = exact.iloc[0]
        matched = True
    else:
        row     = sub.iloc[0] if len(sub) > 0 else agg[agg["Product_Category"] == category].iloc[0]
        matched = False

    # Date-level context (weather/season/peak) from raw data if available
    ctx     = ctx_df[(ctx_df["City"] == city) & (ctx_df["Order_date"].dt.date == chosen_date)]
    season  = ctx["Season"].mode()[0]       if len(ctx) > 0 else row["season"]
    weather = ctx["Weather"].mode()[0]      if len(ctx) > 0 else row["weather"]
    peak_i  = ctx["Peak_Intensity"].mean()  if len(ctx) > 0 else row["peak_intensity"]

    return {
        "city_enc":       bundle["le_city"].transform([city])[0],
        "cat_enc":        bundle["le_cat"].transform([category])[0],
        "avg_demand":     row["avg_demand"],
        "pref_score":     row["pref_score"],
        "peak_intensity": peak_i,
        "is_festival":    int(row["is_festival"]),
        "is_weekend":     int(chosen_date.weekday() >= 5),
        "order_count":    row["order_count"],
        "season_enc":     bundle["le_season"].transform([season])[0],
        "weather_enc":    bundle["le_weather"].transform([weather])[0],
        "month":          chosen_date.month,
        "day_of_year":    chosen_date.timetuple().tm_yday,
    }, matched


def predict_demand(city: str, chosen_date: datetime.date):
    """Predict demand label + share_pct for all 7 categories."""
    results   = {}
    any_exact = True

    for cat in ALL_CATS:
        feat_dict, matched = build_feature_row(city, chosen_date, cat)
        if not matched:
            any_exact = False

        X     = pd.DataFrame([feat_dict])[bundle["features"]]
        label = bundle["model"].predict(X)[0]

        # share_pct for display — exact date if available, else city+category mean
        sub   = agg[(agg["City"] == city) & (agg["Product_Category"] == cat)]
        exact = sub[sub["Order_date"].dt.date == chosen_date]
        share = exact["share_pct"].values[0] if len(exact) > 0 else sub["share_pct"].mean()
        share = round(float(share), 2) if not np.isnan(share) else 0.0

        results[cat] = {"label": label, "share_pct": share}

    return results, any_exact

# ─────────────────────────────────────────────────────────────
# UI — HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("<h2 style='text-align: center; color: white;'> Smart Quick Commerce</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: orange;'>📌 Product Recommendation System</h1>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style='padding: 16px 20px; border-left: 5px solid #4b6bfb; border-radius: 8px; margin-bottom: 20px; color: #c8c8d0;'>
    <b style='color: white;'>🎯 Objective</b><br><br>
    The objective is to suggest trending products based on their past behavior and purchase patterns.
    It enhances inventory optimization. This increases sales, customer engagement,
    and retention.
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────
# UI — FILTERS
# ─────────────────────────────────────────────────────────────
st.markdown("<div class='field-label'>Select City</div>", unsafe_allow_html=True)
city = st.selectbox(
    "city",
    CITIES,
    index=CITIES.index("Chennai") if "Chennai" in CITIES else 0,
    label_visibility="collapsed",
)

st.markdown("<div class='field-label'>Select Date</div>", unsafe_allow_html=True)
chosen_date = st.date_input(
    "date",
    value=datetime.date.today(),
    min_value=datetime.date.today(),
    max_value=datetime.date(2027, 12, 31),
    label_visibility="collapsed",
)

# ─────────────────────────────────────────────────────────────
# PREDICTION
# ─────────────────────────────────────────────────────────────
with st.spinner("Generating recommendations…"):
    results, exact_match = predict_demand(city, chosen_date)

# ─────────────────────────────────────────────────────────────
# BANNER — shown when date is outside dataset range
# ─────────────────────────────────────────────────────────────
if not exact_match:
    st.markdown(
        "<div class='info-banner'>⚠️ No exact data → using closest available pattern</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────────────────────
# UI — DEMAND RECOMMENDATIONS
# ─────────────────────────────────────────────────────────────
st.markdown(
    "<div class='section-header'>📦 &nbsp;Demand-Based Recommendations</div>",
    unsafe_allow_html=True,
)

high_cats   = sorted([(c, v) for c, v in results.items() if v["label"] == "High"],
                     key=lambda x: x[1]["share_pct"], reverse=True)
medium_cats = sorted([(c, v) for c, v in results.items() if v["label"] == "Medium"],
                     key=lambda x: x[1]["share_pct"], reverse=True)
low_cats    = sorted([(c, v) for c, v in results.items() if v["label"] == "Low"],
                     key=lambda x: x[1]["share_pct"], reverse=True)

col_h, col_m, col_l = st.columns(3)

with col_h:
    st.markdown(
        "<div class='col-header-high'>🔥 &nbsp;High Demand (Stock More)</div>",
        unsafe_allow_html=True,
    )
    if high_cats:
        for cat, val in high_cats:
            st.markdown(
                f"<div class='pill-high'>{cat} → {val['share_pct']:.2f}%</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div style='color:#666;font-size:0.85rem;'>No high-demand categories</div>",
            unsafe_allow_html=True,
        )

with col_m:
    st.markdown(
        "<div class='col-header-med'>⚠️ &nbsp;Medium Demand</div>",
        unsafe_allow_html=True,
    )
    if medium_cats:
        for cat, val in medium_cats:
            st.markdown(
                f"<div class='pill-med'>{cat} → {val['share_pct']:.2f}%</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div style='color:#666;font-size:0.85rem;'>No medium-demand categories</div>",
            unsafe_allow_html=True,
        )

with col_l:
    st.markdown(
        "<div class='col-header-low'>✖️ &nbsp;Low Demand (Avoid Overstock)</div>",
        unsafe_allow_html=True,
    )
    if low_cats:
        for cat, val in low_cats:
            st.markdown(
                f"<div class='pill-low'>{cat} → {val['share_pct']:.2f}%</div>",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            "<div style='color:#666;font-size:0.85rem;'>No low-demand categories</div>",
            unsafe_allow_html=True,
        )

# ─────────────────────────────────────────────────────────────
# UI — SMART SUGGESTIONS
# ─────────────────────────────────────────────────────────────
st.markdown(
    "<div class='suggestions-title'>💡 Smart Suggestions</div>",
    unsafe_allow_html=True,
)

suggestions = []

if low_cats:
    low_names = " & ".join([c for c, _ in low_cats[:2]])
    suggestions.append(f"• Avoid overstocking <b>{low_names}</b>")

if high_cats:
    high_names = " & ".join([c for c, _ in high_cats])
    suggestions.append(f"• Pre-stock <b>{high_names}</b> — demand expected to be high in {city}")

if chosen_date.weekday() >= 5:
    suggestions.append("• Weekend detected — increase delivery fleet availability")

if medium_cats:
    med_name = medium_cats[0][0]
    suggestions.append(
        f"• Consider a targeted discount on <b>{med_name}</b> to push it to high demand"
    )

suggestions.append("• Optimize delivery fleet for high-demand categories")

festivals = {10: "Diwali", 8: "Independence Day"}
if chosen_date.month in festivals:
    suggestions.append(
        f"• {festivals[chosen_date.month]} month — expect demand spike across all categories"
    )

for s in suggestions:
    st.markdown(f"<div class='suggestion-item'>{s}</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────
ist = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; background-color: None; border-radius: 8px;'>
    🛒 <b style='color: #aaa;'>Smart Quick Commerce</b> &nbsp;|&nbsp; Product Recommendation Engine &nbsp;|&nbsp; Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b style='color: #bbb;'>{now}</b></i><br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter, personalized inventory decisions.</span>
</div>
""", unsafe_allow_html=True)