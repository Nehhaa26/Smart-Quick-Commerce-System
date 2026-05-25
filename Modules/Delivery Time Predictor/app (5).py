import streamlit as st
import joblib
import pandas as pd
import datetime
import pytz

# =========================================
# LOAD MODELS
# =========================================
model      = joblib.load("delivery_model.pkl")
le_city    = joblib.load("le_city.pkl")
le_traffic = joblib.load("le_traffic.pkl")
le_weather = joblib.load("le_weather.pkl")

# =========================================
# PAGE CONFIG
# =========================================
st.set_page_config(page_title="Delivery Time Predictor", page_icon="🚚", layout="centered")

# =========================================
# CUSTOM STYLING
# =========================================
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"],
[data-testid="stHeader"], section[data-testid="stSidebar"] {
    background-color: #0e0e0e !important;
    color: #e0e0e0 !important;
}
.block-container { padding: 2rem 2rem 2rem 2rem; max-width: 860px; }

[data-testid="stSelectbox"] > div > div,
[data-testid="stDateInput"]  > div > div {
    background-color: #2a2a3e !important;
    border: 1px solid #3a3a5a !important;
    border-radius: 6px !important;
    color: #e0e0e0 !important;
}
[data-testid="stSelectbox"] svg { fill: #a0a0b0 !important; }

.stButton > button {
    height: 50px;
    width: 100%;
    border-radius: 10px;
    font-size: 18px;
    font-weight: bold;
    background-color: #ff4b4b;
    color: white;
}

#MainMenu, footer, [data-testid="stToolbar"] { visibility: hidden; }
div[data-testid="stDecoration"] { display: none; }
[data-testid="stDeployButton"] { visibility: visible !important; }
</style>
""", unsafe_allow_html=True)

# =========================================
# TITLE + SUBTITLE + OBJECTIVE
# =========================================
st.markdown("<h2 style='text-align: center; color: white;'> Smart Quick Commerce</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: orange;'>🚚 Delivery Time Predictor</h1>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style='padding: 16px 20px; border-left: 5px solid #4b6bfb; border-radius: 8px; margin-bottom: 20px; color: #c8c8d0;'>
    <b style='color: white;'>🎯 Objective</b><br><br>
The goal is to predict delivery time and identify possible delays using features like distance, order size, and time. It helps improve delivery efficiency and customer satisfaction. The model enables proactive actions to avoid delays. It supports better logistics planning.
</div>
""", unsafe_allow_html=True)

# =========================================
# SESSION STATE
# =========================================
if "prediction" not in st.session_state:
    st.session_state.prediction = None
if "last_predicted_at" not in st.session_state:
    st.session_state.last_predicted_at = None

# =========================================
# INPUT — main page (no sidebar)
# =========================================
city_list = ['Noida', 'Kolkata', 'Mumbai', 'Jaipur', 'Delhi',
             'Bengluru', 'Pune', 'Amritsar', 'Chennai',
             'Gurgaon', 'Hyderabad', 'Haridwar']

city     = st.selectbox("Select City", city_list)
weather  = st.selectbox("Select Weather", ["Clear", "Rainy"])
distance = st.number_input("Distance (Km)", min_value=1.0, max_value=15.0, value=5.0, step=0.01, format="%.2f")
hour     = st.slider("Order Hour", 0, 23, 20)

# =========================================
# DERIVED FEATURES
# =========================================
def get_peak(hour):
    if 8 <= hour <= 11:    return 2
    elif 18 <= hour <= 22: return 3
    else:                  return 1

def estimate_speed(distance):
    return 25 - (distance * 0.5)

def traffic_level(hour, peak, weekend, festival, speed):
    if (festival == 1 or
            ((hour in range(8, 12) or hour in range(18, 23)) and peak >= 2) or
            speed < 15):
        return "High"
    elif (hour in range(7, 22)) and (peak == 1 or weekend == 1 or speed < 25):
        return "Medium"
    else:
        return "Low"

def estimate_items(distance):
    if distance < 3:    return 2
    elif distance < 7:  return 3
    elif distance < 12: return 4
    else:               return 5

def delivery_status(time):
    if time <= 15:   return "⚡ Very Fast Delivery", "success"
    elif time <= 25: return "🚀 Fast Delivery",      "success"
    elif time <= 40: return "🚦 Moderate Delivery",  "warning"
    else:            return "🐢 Slow Delivery",       "error"

# Compute
peak         = get_peak(hour)
weekend      = 1 if hour >= 18 else 0
festival     = 0
speed        = estimate_speed(distance)
traffic      = traffic_level(hour, peak, weekend, festival, speed)
items        = estimate_items(distance)
items_per_km = items / (distance + 0.01)

# Encode
city_encoded    = le_city.transform([city])[0]
traffic_encoded = le_traffic.transform([traffic])[0]
weather_encoded = le_weather.transform([weather])[0]

# Build input dataframe
input_data = pd.DataFrame({
    'Distance_Km':   [distance],
    'Items_Count':   [items],
    'City':          [city_encoded],
    'Items_per_Km':  [items_per_km],
    'Traffic_Level': [traffic_encoded],
    'Weather':       [weather_encoded],
    'Hour':          [hour]
})

# =========================================
# PREDICTION BUTTON
# =========================================
if st.button("🚀 Predict Delivery Time"):
    pred     = model.predict(input_data)[0]
    pred_int = int(round(pred))
    status, color = delivery_status(pred_int)

    st.session_state.prediction = (pred_int, status, color, traffic)

    ist = pytz.timezone("Asia/Kolkata")
    st.session_state.last_predicted_at = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

# =========================================
# SHOW PREDICTION (PERSISTENT)
# =========================================
if st.session_state.prediction is not None:
    pred_int, status, color, traffic_shown = st.session_state.prediction

    st.success(f"⏱ Estimated Delivery Time: **{pred_int} minutes**")

    if color == "success":
        st.success(status)
    elif color == "warning":
        st.warning(status)
    else:
        st.error(status)

    st.info(f"🚦 Traffic Level: {traffic_shown}")

# =========================================
# FOOTER
# =========================================
ist = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

if st.session_state.last_predicted_at:
    last_pred = st.session_state.last_predicted_at
else:
    last_pred = "No prediction made yet"

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; background-color: none; border-radius: 8px;'>
    🛒 <b style='color: #aaa;'>Smart Quick Commerce</b> &nbsp;|&nbsp; Delivery Time Predictor Engine &nbsp;|&nbsp; Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b style='color: #bbb;'>{now}</b></i> &nbsp;|&nbsp;
    🚀 <i>Last Predicted At: <b style='color: #bbb;'>{last_pred}</b></i><br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter, faster last-mile delivery decisions.</span>
</div>
""", unsafe_allow_html=True)