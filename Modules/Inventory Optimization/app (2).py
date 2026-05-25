# ======================================
# 1. IMPORTS
# ======================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from datetime import date, datetime
import pytz

# ======================================
# 2. PAGE CONFIG
# ======================================
st.set_page_config(page_title="Smart Inventory System", layout="centered")

# ======================================
# 3. LOAD FILES
# ======================================
model = joblib.load("model.pkl")
features = joblib.load("features.pkl")
df = joblib.load("processed_df.pkl")

# ======================================
# 4. SESSION STATE
# ======================================
if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "inventory" not in st.session_state:
    st.session_state.inventory = None

if "show_graph" not in st.session_state:
    st.session_state.show_graph = False

if "last_predicted_at" not in st.session_state:
    st.session_state.last_predicted_at = None

# ======================================
# 5. CUSTOM CSS
# ======================================
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
    background-color: #4CAF50 !important;
    color: white !important;
    border: 2px solid #4CAF50 !important;
}

.stButton > button:active {
    background-color: #4CAF50 !important;
    color: white !important;
    border: 2px solid #4CAF50 !important;
}

.stButton > button:focus {
    background-color: #4CAF50 !important;
    color: white !important;
    border: 2px solid #4CAF50 !important;
    box-shadow: none !important;
}

.kpi-card {
    background-color: #1e2a38;
    border-radius: 12px;
    padding: 18px 12px;
    text-align: center;
    margin-bottom: 12px;
}

.kpi-label {
    color: #9ecbff;
    font-size: 13px;
    margin-bottom: 6px;
    font-weight: 600;
    letter-spacing: 0.5px;
}

.kpi-value {
    color: #ffffff;
    font-size: 28px;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# ======================================
# 6. HEADER
# ======================================
st.markdown("<h2 style='text-align: center; color: white;'>Smart Quick Commerce</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: orange;'>📦 Inventory Optimization</h1>", unsafe_allow_html=True)

st.markdown("---")

# ======================================
# 7. OBJECTIVE
# ======================================
st.markdown("""
<div style='background-color:none; padding: 16px 20px; border-left: 5px solid #4b6bfb; border-radius: 8px; margin-bottom: 20px;'>
    <b>🎯 Objective</b><br><br>
    To predict future product demand and optimize inventory decisions based on historical order patterns,
    location, and category. It helps businesses prevent stock-outs, reduce overstock, and make
    data-driven reorder decisions.
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ======================================
# 8. GET OPTIONS
# ======================================
cities = [col.replace("City_", "") for col in df.columns if col.startswith("City_")]
categories = [col.replace("Product_Category_", "") for col in df.columns if col.startswith("Product_Category_")]

# ======================================
# 9. INPUT SECTION
# ======================================
st.subheader("📥 Input Parameters")

col1, col2 = st.columns(2)

with col1:
    city = st.selectbox("🏙️ Select City", cities)
    selected_date = st.date_input("📅 Select Date", value=date.today())
    current_stock = st.number_input("🏭 Current Stock", min_value=0, value=200, step=1)
    safety_stock = st.number_input("🛡️ Safety Stock", min_value=0, value=50, step=1)

with col2:
    category = st.selectbox("🛒 Select Product Category", categories)
    st.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
    is_festival = st.checkbox("🎉 Is Festival Day?", value=False)
    
st.markdown("---")

# ======================================
# 10. FEATURE BUILDER
# ======================================
def create_features(history, current_date, is_festival):
    row = {}

    row['Day'] = current_date.day
    row['Month'] = current_date.month
    row['Day_of_week'] = current_date.dayofweek
    row['Week_of_Year'] = current_date.isocalendar().week
    row['Is_Weekend'] = 1 if current_date.dayofweek >= 5 else 0
    row['Season'] = (current_date.month % 12 // 3)
    row['Is_Festival'] = 1 if is_festival else 0

    row['lag_1'] = history[-1]
    row['lag_2'] = history[-2]
    row['lag_3'] = history[-3]
    row['lag_7'] = history[-7]
    row['lag_14'] = history[-14]

    row['rolling_mean_7'] = np.mean(history[-7:])

    row_df = pd.DataFrame([row])

    for col in features:
        if col not in row_df.columns:
            row_df[col] = 0

    return row_df[features]

# ======================================
# 11. DEMAND PREDICTION
# ======================================
def predict_demand(city, category, selected_date, is_festival):

    selected_date = pd.to_datetime(selected_date)

    temp = df[(df['City_' + city] == 1) & (df['Product_Category_' + category] == 1)]
    temp = temp.sort_values(by='Order_date')

    history = list(temp[temp['Order_date'] < selected_date]['Items_Count'].tail(14))

    if len(history) < 14:
        return None, "Not enough data"

    row_df = create_features(history, selected_date, is_festival)

    row_df['City_' + city] = 1
    row_df['Product_Category_' + category] = 1

    row_df = row_df[features]

    pred = np.expm1(model.predict(row_df))[0]

    return int(pred), None

# ======================================
# 12. INVENTORY LOGIC
# ======================================
def inventory_decision(predicted_demand, current_stock, safety_stock):

    required_stock = predicted_demand + safety_stock

    if current_stock < predicted_demand:
        status = "🔴 Stock-Out Risk"
    elif current_stock > predicted_demand * 1.5:
        status = "🟡 Overstock"
    else:
        status = "🟢 Sufficient"

    if predicted_demand == 0:
        risk = 0
    else:
        risk = max(0, (predicted_demand - current_stock) / predicted_demand * 100)

    reorder_qty = max(0, required_stock - current_stock)

    return status, round(risk, 2), required_stock, reorder_qty

# ======================================
# 13. 7-DAY FORECAST
# ======================================
def generate_7_day_data(city, category, selected_date, is_festival):

    dates = []
    values = []

    for i in range(-3, 4):
        d = pd.to_datetime(selected_date) + pd.Timedelta(days=i)

        pred, error = predict_demand(city, category, d, is_festival)

        if error:
            return None, None, error

        dates.append(d)
        values.append(pred)

    return dates, values, None

# ======================================
# 14. BUTTONS
# ======================================
col1, col2 = st.columns(2)

with col1:
    if st.button("🔮 Predict Demand + Inventory"):

        pred, error = predict_demand(city, category, selected_date, is_festival)

        if error:
            st.warning(error)
        else:
            status, risk, required, reorder = inventory_decision(
                pred, current_stock, safety_stock
            )

            st.session_state.prediction = pred
            st.session_state.inventory = (status, risk, required, reorder)
            ist = pytz.timezone("Asia/Kolkata")
            st.session_state.last_predicted_at = datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

with col2:
    if st.button("📈 Show 7 Days Forecast"):
        st.session_state.show_graph = True

# ======================================
# 15. KPI RESULTS
# ======================================
if st.session_state.prediction is not None:

    st.markdown("#### 📊 Demand & Inventory Results")

    status, risk, required, reorder = st.session_state.inventory

    # Row 1 — 3 KPIs
    k1, k2, k3 = st.columns(3)

    with k1:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>📦 Predicted Demand</div>
            <div class='kpi-value'>{st.session_state.prediction}</div>
        </div>""", unsafe_allow_html=True)

    with k2:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>🚦 Stock Status</div>
            <div class='kpi-value' style='font-size:20px;'>{status}</div>
        </div>""", unsafe_allow_html=True)

    with k3:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>⚠️ Stock-Out Risk</div>
            <div class='kpi-value'>{risk}%</div>
        </div>""", unsafe_allow_html=True)

    # Row 2 — 2 KPIs
    k4, k5 = st.columns(2)

    with k4:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>🏭 Required Stock</div>
            <div class='kpi-value'>{required}</div>
        </div>""", unsafe_allow_html=True)

    with k5:
        st.markdown(f"""
        <div class='kpi-card'>
            <div class='kpi-label'>🔁 Reorder Quantity</div>
            <div class='kpi-value'>{reorder}</div>
        </div>""", unsafe_allow_html=True)

    # Suggestion
    st.markdown("### 💡 Suggestion")

    if "Stock-Out" in status:
        st.error("⚠️ Increase stock immediately to avoid stock-out.")
    elif "Overstock" in status:
        st.warning("📦 Reduce stock or apply discounts to clear inventory.")
    else:
        st.success("✅ Inventory is well balanced.")

    st.markdown("---")

# ======================================
# 16. GRAPH (FIXED SIZE)
# ======================================
if st.session_state.show_graph:

    dates, values, error = generate_7_day_data(city, category, selected_date, is_festival)

    if error:
        st.warning(error)
    else:
        fig, ax = plt.subplots(figsize=(8, 4))

        ax.plot(dates, values, marker='o', color='#ff4b4b', linewidth=2, markersize=6)
        ax.axvline(pd.to_datetime(selected_date), linestyle='--', color='orange', label='Selected Date')

        ax.set_title("7-Day Demand Forecast", fontsize=14, fontweight='bold')
        ax.set_xlabel("Date", fontsize=11)
        ax.set_ylabel("Demand (Units)", fontsize=11)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.4)

        plt.xticks(rotation=45)
        plt.tight_layout()

        st.pyplot(fig, use_container_width=True)

# ======================================
# 17. FOOTER
# ======================================
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

last_pred = st.session_state.last_predicted_at if st.session_state.last_predicted_at else "No prediction made yet"

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; border-radius: 8px;'>
    📦 <b>Smart Inventory System</b> &nbsp;|&nbsp; Inventory Optimization Engine &nbsp;|&nbsp;
    Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b>{now}</b></i> &nbsp;|&nbsp;
    🔮 <i>Last Predicted At: <b>{last_pred}</b></i> <br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter inventory decisions.</span>
</div>
""", unsafe_allow_html=True)