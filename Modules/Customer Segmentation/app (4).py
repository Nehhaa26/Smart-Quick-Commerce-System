# =========================================
# 📦 IMPORT LIBRARIES
# =========================================
import streamlit as st
import numpy as np
import joblib
from datetime import datetime
import pytz

# =========================================
# LOAD FILES
# =========================================
scaler = joblib.load("scaler.pkl")
features = joblib.load("features.pkl")

try:
    model = joblib.load("gmm_model.pkl")
    model_type = "GMM"
except:
    model = joblib.load("kmeans_model.pkl")
    model_type = "KMeans"

# =========================================
# 🎨 PAGE CONFIG
# =========================================
st.set_page_config(
    page_title="Customer Segmentation",
    page_icon="🧠",
    layout="centered"
)

# =========================================
# 🎨 CUSTOM CSS
# =========================================
st.markdown("""
<style>
.stButton > button {
    height: 50px;
    width: 100%;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    background-color: #ff4b4b;
    color: white;
}

.stButton > button:hover {
    background-color: #cc0000;
    color: white !important;
    border: 2px solid #ff4b4b;
}

.stNumberInput>div>div>input {
    border-radius: 8px;
}

.result-box {
    padding: 15px;
    border-radius: 10px;
    background-color: #1f3d2b;
    color: #00ff9c;
    font-size: 18px;
    text-align: center;
}

.info-box {
    padding: 12px;
    border-radius: 10px;
    background-color: #1e2a38;
    color: #9ecbff;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# =========================================
# 🧠 HEADER
# =========================================
st.markdown("<h2 style='text-align: center; color: white;'>Smart Quick Commerce</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: orange;'>🧠 Customer Segmentation</h1>", unsafe_allow_html=True)

st.markdown("---")

# =========================================
# 🎯 OBJECTIVE SECTION
# =========================================
st.markdown("""
<div style='background-color:none; padding: 16px 20px; border-left: 5px solid #4b6bfb; border-radius: 8px; margin-bottom: 20px;'>
    <b>🎯 Objective</b><br><br>
    To classify customers into meaningful segments based on their purchase behavior — including recency,
    frequency, and monetary value. This enables targeted marketing, personalized engagement, and
    improved customer retention strategies.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# =========================================
# 📥 INPUT SECTION (IN COLUMNS)
# =========================================
st.subheader("📥 Customer Details")

col1, col2 = st.columns(2)

with col1:
    recency = st.number_input("📅 Recency (days)", min_value=0, max_value=100, step=1)
    monetary = st.number_input("💰 Total Spend", min_value=0.0, max_value=18000.0)
    items = st.number_input("📦 Items Count", min_value=0, max_value=150, step=1)

with col2:
    frequency = int(st.number_input("🔁 Total Orders", min_value=0, max_value=15, step=1))
    discount = st.number_input("🏷️ Discount Usage Rate", min_value=0.0, max_value=1.0)

# Default rating
rating = 3.8

st.markdown("---")

# =========================================
# 🚀 PREDICTION BUTTON
# =========================================
if st.button("🔍 Predict Customer Segment"):

    # Transform
    recency_log = np.log1p(recency)
    frequency_log = np.log1p(frequency)
    monetary_log = np.log1p(monetary)

    input_data = np.array([[
        recency_log,
        frequency_log,
        monetary_log,
        items,
        rating,
        discount
    ]])

    # Scale
    input_scaled = scaler.transform(input_data)

    # Predict
    segment = model.predict(input_scaled)[0]

    segment_map = {
        0: "Low Value Customer",
        1: "High Value Customer"
    }

    label = segment_map.get(segment)

    # =========================================
    # 🎯 RESULT DISPLAY (STYLED)
    # =========================================
    st.markdown(
        f"<div class='result-box'>🎯 Segment: {label}</div>",
        unsafe_allow_html=True
    )

    # Insight
    if segment == 1:
        st.markdown(
            "<div class='info-box'>💡 High-value customer — focus on retention & loyalty.</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            "<div class='info-box'>💡 Low engagement — target with offers & campaigns.</div>",
            unsafe_allow_html=True
        )

# =========================================
# 13. FOOTER
# =========================================
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; background-color: none; border-radius: 8px;'>
    🧠 <b>Smart Customer Analytics</b> &nbsp;|&nbsp; Customer Segmentation Engine &nbsp;|&nbsp;
    Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b>{now}</b></i> <br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter customer engagement decisions.</span>
</div>
""", unsafe_allow_html=True)