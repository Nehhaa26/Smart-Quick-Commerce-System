import streamlit as st
import subprocess
import sys
import os
import datetime
import pytz

st.set_page_config(
    page_title="Quick Commerce Home Page",
    page_icon="📦",
    layout="centered",
    initial_sidebar_state="collapsed",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CATEGORIES = {
    "Prediction UI": {
        "icon": "📊",
        "label": "Prediction Modules",
        "modules": [
            "Demand Forecasting",
            "Delivery Performance Prediction",
            "Recommendation System",
        ],
    },
    "Visualization UI": {
        "icon": "📉",
        "label": "Visualization Modules",
        "modules": [
            "Customer Behaviour Analysis",
            "Sentiment Analysis",
            "Logistic Analysis",
        ],
    },
    "Decision UI": {
        "icon": "🧠",
        "label": "Decision Modules",
        "modules": [
            "Inventory Optimization",
            "Customer Segmentation",
        ],
    },
}

# ── Session state ──────────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "home"
if "launched" not in st.session_state:
    st.session_state.launched = None

# ── Per-page layout CSS ────────────────────────────────────────────────────────
if st.session_state.page == "home":
    st.markdown("""
    <style>
    [data-testid="stAppViewBlockContainer"] {
        max-width: 80% !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    [data-testid="stAppViewBlockContainer"] {
        max-width: 860px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* global dark background */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stHeader"] {
    background-color: #0e0e0e !important;
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] { display: none !important; }
section[data-testid="stSidebar"] { display: none !important; }

.block-container { padding: 1rem 2rem !important; }

/* home page — 80% of page, centered */
.home-page { max-width: 80%; margin: 0 auto; }

/* category page — narrow centered like original centered layout */
.centered-page { max-width: 720px; margin: 0 auto; }

/* ── HERO ── */
.hero {
    background: linear-gradient(135deg, #0f0c29, #1a1a4e, #24243e);
    border: 1px solid #2a2a5a;
    border-radius: 20px;
    padding: 3rem 2.5rem 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; left: -60px;
    width: 220px; height: 220px;
    background: radial-gradient(circle, #4b6bfb33, transparent 70%);
    border-radius: 50%;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -60px; right: -60px;
    width: 200px; height: 200px;
    background: radial-gradient(circle, #f9731633, transparent 70%);
    border-radius: 50%;
}
.hero-badge {
    display: inline-block;
    background: #4b6bfb22;
    border: 1px solid #4b6bfb66;
    color: #93c5fd;
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-title {
    font-size: 2.8rem;
    font-weight: 900;
    color: #ffffff;
    line-height: 1.1;
    margin-bottom: 0.6rem;
    letter-spacing: -1.5px;
}
.hero-title span { color: #f97316; }
.hero-sub {
    font-size: 1rem;
    color: #94a3b8;
    max-width: 540px;
    margin: 0 auto 1.6rem;
    line-height: 1.7;
}

/* ── STATS ROW ── */
.stat-row {
    display: flex;
    justify-content: center;
    gap: 2.5rem;
    margin-top: 1.6rem;
    flex-wrap: wrap;
}
.stat-item { text-align: center; }
.stat-num  { font-size: 2rem; font-weight: 900; color: #f97316; }
.stat-lbl  { font-size: 0.85rem; color: #cbd5e1; letter-spacing: 0.5px; text-transform: uppercase; font-weight: 800; }

/* ── FEATURE STRIP ── */
.feature-strip {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;
    flex-wrap: wrap;
}
.feature-pill {
    background: #1c1c2e;
    border: 1px solid #2a2a4a;
    border-radius: 10px;
    padding: 0.7rem 1rem;
    flex: 1;
    min-width: 160px;
    text-align: center;
}
.feature-pill-icon { font-size: 1.4rem; display: block; margin-bottom: 0.3rem; }
.feature-pill-text { font-size: 0.78rem; color: #94a3b8; line-height: 1.4; }
.feature-pill-title { font-size: 0.85rem; font-weight: 700; color: #e2e8f0; margin-bottom: 0.2rem; }

/* ── SECTION LABEL ── */
.section-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #4b6bfb;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.section-title {
    font-size: 1.4rem;
    font-weight: 800;
    color: #f1f5f9;
    margin-bottom: 1.4rem;
}

/* category cards — fixed equal height for all */
.cat-card {
    background: #1c1c2e;
    border: 1px solid #2a2a4a;
    border-radius: 14px;
    padding: 1.4rem;
    text-align: center;
    height: 300px;
    overflow: hidden;
    transition: border-color 0.2s;
    box-sizing: border-box;
}
.cat-card:hover { border-color: #4b6bfb; }
.cat-icon  { font-size: 2.6rem; margin-bottom: 0.4rem; display: block; }
.cat-name  { font-weight: 700; font-size: 1.05rem; color: #f1f5f9; margin: 0.4rem 0; }
.cat-count { font-size: 0.78rem; color: #64748b; margin-bottom: 0.5rem; }
.cat-list  { text-align: left; padding-left: 1.2rem;
             color: #94a3b8; font-size: 0.82rem; margin-top: 0.6rem; }

/* module buttons */
.stButton > button {
    background: #1c1c2e !important;
    border: 1px solid #2a2a4a !important;
    color: #e2e8f0 !important;
    border-radius: 10px !important;
    padding: 0.7rem 1.2rem !important;
    font-size: 1rem !important;
    font-weight: 500 !important;
    width: 100%;
    text-align: center !important;
    transition: border-color 0.2s, color 0.2s;
    height: 52px;
}
.stButton > button:hover {
    border-color: #4b6bfb !important;
    color: #93c5fd !important;
    background: #1a2035 !important;
}

/* back button — teal pill, distinct from all other buttons */
.back-btn .stButton > button {
    background: linear-gradient(135deg, #0f2027, #1a3a3a) !important;
    border: 2px solid #2dd4bf !important;
    color: #2dd4bf !important;
    border-radius: 25px !important;
    padding: 0.5rem 1.6rem !important;
    height: auto !important;
    font-size: 0.92rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.5px !important;
    width: auto !important;
    transition: all 0.2s !important;
}
.back-btn .stButton > button:hover {
    background: #2dd4bf !important;
    color: #0e0e0e !important;
    border-color: #2dd4bf !important;
}

/* open button under cards */
.open-btn .stButton > button {
    background: #1c1c2e !important;
    border: 1px solid #2a2a4a !important;
    color: #e2e8f0 !important;
    border-radius: 8px !important;
    height: 46px !important;
    font-size: 0.92rem !important;
}

/* success launch box */
.launch-success {
    background: #14532d;
    border: 1px solid #166534;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    color: #86efac;
    font-size: 0.9rem;
    margin-top: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ── HOME PAGE ──────────────────────────────────────────────────────────────────
if st.session_state.page == "home":

    st.markdown("<div class='home-page'>", unsafe_allow_html=True)

    # ── HERO ──────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class='hero'>
        <div class='hero-badge'>🚀 Data Driven Solution</div>
        <div class='hero-title'>Smart <span>Quick Commerce</span><br>Intelligence Hub</div>
        <div class='hero-sub'>
            One unified platform to predict, visualize, and decide — powered by machine learning,
            built for the speed of modern quick commerce.
        </div>
       <div class='stat-row'>
    <div class='stat-item'>
        <div class='stat-num'><b>8</b></div>
        <div class='stat-lbl'><b>Total Modules</b></div>
    </div>
    <div class='stat-item'>
        <div class='stat-num'><b>3</b></div>
        <div class='stat-lbl'><b>Module Types</b></div>
    </div>
    <div class='stat-item'>
        <div class='stat-num'><b>12</b></div>
        <div class='stat-lbl'><b>Cities</b></div>
    </div>
    <div class='stat-item'>
        <div class='stat-num'><b>8</b></div>
        <div class='stat-lbl'><b>Companies</b></div>
    </div>
    <div class='stat-item'>
        <div class='stat-num'><b>3M</b></div>
        <div class='stat-lbl'><b>Total Data</b></div>
    </div>
 </div>
</div>
    """, unsafe_allow_html=True)

    # ── FEATURE HIGHLIGHTS ────────────────────────────────────────────────────
    st.markdown("""
    <div class='feature-strip'>
        <div class='feature-pill'>
            <span class='feature-pill-icon'>🔮</span>
            <div class='feature-pill-title'>Predict</div>
            <div class='feature-pill-text'>Forecast demand, delivery times & recommendations</div>
        </div>
        <div class='feature-pill'>
            <span class='feature-pill-icon'>📊</span>
            <div class='feature-pill-title'>Visualize</div>
            <div class='feature-pill-text'>Analyze behavior, sentiment & logistics trends</div>
        </div>
        <div class='feature-pill'>
            <span class='feature-pill-icon'>🧠</span>
            <div class='feature-pill-title'>Decide</div>
            <div class='feature-pill-text'>Optimize inventory & segment customers intelligently</div>
        </div>
        <div class='feature-pill'>
            <span class='feature-pill-icon'>⚡</span>
            <div class='feature-pill-title'>Real-time</div>
            <div class='feature-pill-text'>Live IST timestamps and session-aware results</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── MODULE CARDS ──────────────────────────────────────────────────────────
    st.markdown("<div class='section-label'>Explore Modules</div>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>Choose a module type to get started</div>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, (cat_name, cat_data) in enumerate(CATEGORIES.items()):
        with cols[i]:
            st.markdown(f"""
            <div class='cat-card'>
                <div class='cat-icon'>{cat_data['icon']}</div>
                <div class='cat-name'>{cat_name}</div>
                <div class='cat-count'>{len(cat_data['modules'])} modules</div>
                <ul class='cat-list'>
                    {''.join(f'<li>{m}</li>' for m in cat_data['modules'])}
                </ul>
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            st.markdown('<div class="open-btn">', unsafe_allow_html=True)
            if st.button(f"Open {cat_name}", key=f"home_{cat_name}", use_container_width=True):
                st.session_state.page = cat_name
                st.session_state.launched = None
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # close home-page

# ── CATEGORY PAGE ──────────────────────────────────────────────────────────────
else:
    st.markdown("<div class='centered-page'>", unsafe_allow_html=True)
    cat = CATEGORIES[st.session_state.page]

    st.markdown("<h1 style='text-align: center; color: orange; font-size: 2.4rem; font-weight: 900;'>Smart Quick Commerce Modules</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown(f"<h3 style='color: white;'>{cat['icon']} {cat['label']}</h3>", unsafe_allow_html=True)
    st.markdown("<p style='color: #94a3b8; margin-bottom: 1rem;'><b>Select a module to launch:</b></p>", unsafe_allow_html=True)

    for module in cat["modules"]:
        if st.button(module, key=f"mod_{module}", use_container_width=True):
            app_path = os.path.join(BASE_DIR, module, "app.py")
            if os.path.isfile(app_path):
                subprocess.Popen(
                    [sys.executable, "-m", "streamlit", "run", app_path],
                    cwd=os.path.join(BASE_DIR, module)
                )
                st.session_state.launched = module
            else:
                st.session_state.launched = f"ERROR: app.py not found in '{module}'"
            st.rerun()

    if st.session_state.launched:
        if st.session_state.launched.startswith("ERROR"):
            st.error(f"❌ {st.session_state.launched}")
        else:
            st.markdown(
                f"<div class='launch-success'>✅ Launching: <b>{st.session_state.launched}</b> — check your browser for the new tab.</div>",
                unsafe_allow_html=True
            )

    # Back to Home button — below modules
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="back-btn">', unsafe_allow_html=True)
    if st.button("← Back to Home", use_container_width=True):
        st.session_state.page = "home"
        st.session_state.launched = None
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # close centered-page

# ── Footer ─────────────────────────────────────────────────────────────────────
ist = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

st.markdown("<div class='centered-page'>", unsafe_allow_html=True)
st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; background-color:none; border-radius: 8px;'>
    🛒 <b style='color: #aaa;'>Smart Quick Commerce</b> &nbsp;|&nbsp; Access to all modules &nbsp;|&nbsp; Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b style='color: #bbb;'>{now}</b></i><br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter quick commerce decisions.</span>
</div>
""", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)