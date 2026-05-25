# ==============================
# 1. IMPORTS
# ==============================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
from datetime import date, datetime
import pytz

# ==============================
# 2. PAGE CONFIG
# ==============================
st.set_page_config(page_title="Demand Forecasting", layout="centered")

# ==============================
# 3. CUSTOM STYLING (BUTTONS)
# ==============================
st.markdown("""
<style>
.stButton > button {
    height: 50px;
    width: 100%;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
}

.predict-btn button {
    background-color: #ff4b4b;
    color: white;
}

.graph-btn button {
    background-color: #4CAF50;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ==============================
# 4. LOAD FILES
# ==============================
model = joblib.load("model.pkl")
features = joblib.load("features.pkl")
df = joblib.load("processed_df.pkl")

# ==============================
# 5. SESSION STATE (IMPORTANT)
# ==============================
if "prediction" not in st.session_state:
    st.session_state.prediction = None

if "last_predicted_at" not in st.session_state:
    st.session_state.last_predicted_at = None

# ==============================
# 6. UI
# ==============================
st.markdown("<h2 style='text-align: center; color: white;'>Smart Quick Commerce</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: orange;'>📦 Demand Forecasting Prediction</h1>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style='background-color:none; padding: 16px 20px; border-left: 5px solid #4b6bfb; border-radius: 8px; margin-bottom: 20px;'>
    <b>🎯 Objective</b><br><br>
    To predict future product demand based on historical order patterns, location, and category.
    It helps businesses anticipate customer needs and plan stock accordingly. This reduces stock-outs
    and improves service availability.
</div>
""", unsafe_allow_html=True)

cities = [col.replace("City_", "") for col in df.columns if col.startswith("City_")]
categories = [col.replace("Product_Category_", "") for col in df.columns if col.startswith("Product_Category_")]

city = st.selectbox("Select City", cities)
category = st.selectbox("Select Product Category", categories)

today = date.today()
max_date = date(2027, 12, 31)

date_selected = st.date_input(
    "Select Date",
    min_value=today,
    max_value=max_date,
    value=today
)

is_festival = st.checkbox("🎉 Is Festival Day?", value=False)

# ==============================
# 7. FEATURE BUILDER
# ==============================
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

# ==============================
# 8. PREDICTION
# ==============================
def predict_demand(city, category, date, is_festival):

    date = pd.to_datetime(date)

    temp = df[(df['City_' + city] == 1) & (df['Product_Category_' + category] == 1)]
    temp = temp.sort_values(by='Order_date')

    history = list(temp[temp['Order_date'] < date]['Items_Count'].tail(14))

    if len(history) < 14:
        return None, "Not enough data"

    row_df = create_features(history, date, is_festival)

    row_df['City_' + city] = 1
    row_df['Product_Category_' + category] = 1

    row_df = row_df[features]

    pred = np.expm1(model.predict(row_df))[0]

    return int(pred), None

# ==============================
# 9. GRAPH DATA (FIXED LOGIC)
# ==============================
def generate_7_day_data(city, category, selected_date, is_festival):

    selected_date = pd.to_datetime(selected_date)

    dates = []
    values = []

    start_date = selected_date - pd.Timedelta(days=3)

    for i in range(7):
        current_date = start_date + pd.Timedelta(days=i)

        pred, error = predict_demand(city, category, current_date, is_festival)

        if error:
            return None, None, error

        dates.append(current_date)
        values.append(pred)

    return dates, values, None

# ==============================
# 10. BUTTONS (SIDE BY SIDE)
# ==============================
col1, col2 = st.columns(2)

with col1:
    if st.button("🔮 Predict Demand"):
        result, error = predict_demand(city, category, date_selected, is_festival)

        if error:
            st.warning(error)
        else:
            st.session_state.prediction = result
            ist = pytz.timezone("Asia/Kolkata")
            st.session_state.last_predicted_at = datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

with col2:
    if st.button("📈 Show Graph"):
        st.session_state.show_graph = True

# ==============================
# 11. SHOW PREDICTION (PERSISTENT)
# ==============================
if st.session_state.prediction is not None:
    st.success(f"📊 Predicted Demand: {st.session_state.prediction} units")

# ==============================
# 12. SHOW GRAPH
# ==============================
if st.session_state.get("show_graph", False):

    dates, values, error = generate_7_day_data(city, category, date_selected, is_festival)

    if error:
        st.warning(error)
    else:
        fig, ax = plt.subplots()

        ax.plot(dates, values, marker='o')

        ax.axvline(pd.to_datetime(date_selected), linestyle='--')

        ax.set_title("7-Day Demand (Forecast Window)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Demand")

        plt.xticks(rotation=45)

        st.pyplot(fig)

# ==============================
# 13. FOOTER
# ==============================
ist = pytz.timezone("Asia/Kolkata")
now = datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

if st.session_state.last_predicted_at:
    last_pred = st.session_state.last_predicted_at
else:
    last_pred = "No prediction made yet"

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; background-color: none; border-radius: 8px;'>
    🛒 <b>Smart Quick Commerce</b> &nbsp;|&nbsp; Demand Forecasting Engine &nbsp;|&nbsp;
    Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b>{now}</b></i> &nbsp;|&nbsp;
    🔮 <i>Last Predicted At: <b>{last_pred}</b></i> <br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter inventory decisions.</span>
</div>
""", unsafe_allow_html=True)