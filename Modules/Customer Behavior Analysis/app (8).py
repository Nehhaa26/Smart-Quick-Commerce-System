# final_perfect_dashboard_fixed.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import datetime
import pytz

st.set_page_config(page_title="Customer Analytics", layout="centered")

# -----------------------------
# CSS
# -----------------------------
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #0e0e0e !important;
    color: #e0e0e0 !important;
}
.block-container { padding: 2rem 2rem 2rem 2rem; max-width: 960px; }

.metric-card {
    background: linear-gradient(135deg, #1f2937, #111827);
    padding: 18px 20px;
    border-radius: 14px;
    color: white;
    height: 130px;

    display: flex;
    flex-direction: column;
    justify-content: space-between;

    box-shadow: 0 6px 16px rgba(0,0,0,0.5);
    transition: 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-6px);
}

.metric-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    opacity: 0.85;
}

.metric-value {
    font-size: 30px;
    font-weight: 700;
    letter-spacing: 1px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# FORMAT FUNCTION
# -----------------------------
def format_number(num):
    if num >= 1e7:
        return f"{num/1e7:.1f}Cr"
    elif num >= 1e5:
        return f"{num/1e5:.1f}L"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K"
    return str(int(num))

# -----------------------------
# LOAD DATA
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("QCFE6_Perfect_Customer_Behaviour.csv")
    df = df.sample(200000, random_state=42)
    df['Order_date'] = pd.to_datetime(df['Order_date'], errors='coerce')
    return df

df = load_data()

# -----------------------------
# RFM FUNCTION (FIXED POSITION)
# -----------------------------
@st.cache_data
def compute_rfm(data):
    today = data['Order_date'].max()

    rfm = data.groupby('Customer_ID').agg({
        'Order_date': lambda x: (today - x.max()).days,
        'Order_ID': 'count',
        'Total_Spend': 'sum'
    }).reset_index()

    rfm.columns = ['Customer_ID','Recency','Frequency','Monetary']

    rfm['R'] = pd.qcut(rfm['Recency'],4,labels=[4,3,2,1],duplicates='drop')
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'),4,labels=[1,2,3,4],duplicates='drop')
    rfm['M'] = pd.qcut(rfm['Monetary'],4,labels=[1,2,3,4],duplicates='drop')

    rfm['Segment']="Others"
    rfm.loc[(rfm['R']==4)&(rfm['F']==4)&(rfm['M']==4),'Segment']="Champions"
    rfm.loc[(rfm['F']>=3)&(rfm['M']>=3),'Segment']="Loyal"
    rfm.loc[(rfm['R']>=3),'Segment']="Recent"
    rfm.loc[(rfm['R']<=2),'Segment']="At Risk"

    return rfm

# ── TITLE + SUBTITLE + OBJECTIVE ─────────────────────────────────────────────
st.markdown("<h2 style='text-align: center; color: white;'>🛒 Smart Quick Commerce</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: orange;'>🔥 Customer Behavior Analysis Dashboard</h1>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style='padding: 16px 20px; border-left: 5px solid #4b6bfb; border-radius: 8px; margin-bottom: 20px; color: #c8c8d0;'>
    <b style='color: white;'>🎯 Objective</b><br><br>
    The objective is to analyze customer behavior, segmentation, and revenue trends across cities and
    product categories in the quick commerce space. It helps businesses identify high-value customers,
    understand purchase patterns, and optimize retention strategies. This enables data-driven decisions
    to improve customer lifetime value, reduce churn, and drive personalized engagement.
</div>
""", unsafe_allow_html=True)

# ── Inline filters (multiselect, no sidebar) ──────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    city = st.multiselect("🏙️ Select City", df['City'].unique(), default=list(df['City'].unique()))
with col_f2:
    category = st.multiselect("🛒 Select Product Category", df['Product_Category'].unique(), default=list(df['Product_Category'].unique()))

df = df[(df['City'].isin(city)) & (df['Product_Category'].isin(category))]

rfm = compute_rfm(df)

# -----------------------------
# KPI (UPGRADED)
# -----------------------------
# Current period
total_customers = df['Customer_ID'].nunique()
total_revenue = df['Total_Spend'].sum()
avg_order = df['Order_Value'].mean()
orders = len(df)

# Previous period (for comparison)
prev_df = df[df['Order_date'] < df['Order_date'].quantile(0.5)]

prev_customers = prev_df['Customer_ID'].nunique()
prev_revenue = prev_df['Total_Spend'].sum()

# Growth %
cust_growth = ((total_customers - prev_customers) / prev_customers * 100) if prev_customers else 0
rev_growth = ((total_revenue - prev_revenue) / prev_revenue * 100) if prev_revenue else 0

# Retention
repeat_users = rfm[rfm['Frequency'] > 1]['Customer_ID'].nunique()
retention_rate = (repeat_users / total_customers) * 100 if total_customers else 0

c1, c2, c3, c4, c5 = st.columns(5)

def trend(val):
    return f"▲ {val:.1f}%" if val >= 0 else f"▼ {abs(val):.1f}%"

c1.markdown(f"""
<div class='metric-card'>
<div class='metric-header'>👥 Customers</div>
<div class='metric-value'>{format_number(total_customers)}</div>
<div style='font-size:12px;color:#9ca3af'>{trend(cust_growth)}</div>
</div>
""", unsafe_allow_html=True)

c2.markdown(f"""
<div class='metric-card'>
<div class='metric-header'>💰 Revenue</div>
<div class='metric-value'>₹{format_number(total_revenue)}</div>
<div style='font-size:12px;color:#9ca3af'>{trend(rev_growth)}</div>
</div>
""", unsafe_allow_html=True)

c3.markdown(f"""
<div class='metric-card'>
<div class='metric-header'>🧾 Avg Order</div>
<div class='metric-value'>₹{avg_order:,.0f}</div>
</div>
""", unsafe_allow_html=True)

c4.markdown(f"""
<div class='metric-card'>
<div class='metric-header'>📦 Orders</div>
<div class='metric-value'>{format_number(orders)}</div>
</div>
""", unsafe_allow_html=True)

c5.markdown(f"""
<div class='metric-card'>
<div class='metric-header'>🔁 Retention</div>
<div class='metric-value'>{retention_rate:.1f}%</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# RFM
# -----------------------------

rfm = compute_rfm(df)
@st.cache_data
def compute_rfm(data):
    today = data['Order_date'].max()

    rfm = data.groupby('Customer_ID').agg({
        'Order_date': lambda x: (today - x.max()).days,
        'Order_ID': 'count',
        'Total_Spend': 'sum'
    }).reset_index()

    rfm.columns = ['Customer_ID','Recency','Frequency','Monetary']

    rfm['R'] = pd.qcut(rfm['Recency'],4,labels=[4,3,2,1],duplicates='drop')
    rfm['F'] = pd.qcut(rfm['Frequency'].rank(method='first'),4,labels=[1,2,3,4],duplicates='drop')
    rfm['M'] = pd.qcut(rfm['Monetary'],4,labels=[1,2,3,4],duplicates='drop')

    rfm['Segment']="Others"
    rfm.loc[(rfm['R']==4)&(rfm['F']==4)&(rfm['M']==4),'Segment']="Champions"
    rfm.loc[(rfm['F']>=3)&(rfm['M']>=3),'Segment']="Loyal"
    rfm.loc[(rfm['R']>=3),'Segment']="Recent"
    rfm.loc[(rfm['R']<=2),'Segment']="At Risk"

    return rfm

# =========================================================
# 🎯 1. SEGMENTATION (FIXED PROPERLY)
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🎯 Customer Segmentation")

seg_df = (rfm['Segment'].value_counts(normalize=True)*100).reset_index()
seg_df.columns = ['Segment','Percent']
seg_df = seg_df.sort_values(by='Percent', ascending=False)

fig = px.bar(
    seg_df,
    x='Segment',
    y='Percent',
    color='Segment',
    text='Percent',
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_traces(
    texttemplate='%{text:.1f}%',
    textposition='outside'
)

fig.update_layout(
    xaxis_title="Customer Segment",
    yaxis_title="% Customers",
    legend_title_text=''
)

st.plotly_chart(fig, use_container_width=True)

# Insight added
top_seg = seg_df.iloc[0]
st.info(f"📊 {top_seg['Segment']} dominates ({top_seg['Percent']:.1f}%). Focus retention strategy here.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 💰 SEGMENT vs REVENUE (NEW - IMPORTANT)
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("💰 Revenue Contribution by Segment")

seg_rev = rfm.groupby('Segment')['Monetary'].sum().reset_index()
seg_rev = seg_rev.sort_values(by='Monetary', ascending=False)

fig = px.bar(
    seg_rev,
    x='Segment',
    y='Monetary',
    color='Segment',
    text='Monetary',
    color_discrete_sequence=px.colors.qualitative.Set2
)

fig.update_traces(
    texttemplate='₹%{text:,.0f}',
    textposition='outside'
)

fig.update_layout(
    xaxis_title="Customer Segment",
    yaxis_title="Total Revenue (₹)"
)

st.plotly_chart(fig, use_container_width=True)

top_seg = seg_rev.iloc[0]
st.success(f"💰 '{top_seg['Segment']}' segment contributes highest revenue — focus here for business impact.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 💎 CUSTOMER LIFETIME VALUE (NEW)
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("💎 Customer Lifetime Value")

rfm['CLV'] = rfm['Monetary'] / rfm['Frequency']

fig = px.histogram(rfm, x='CLV', nbins=50)

st.plotly_chart(fig, use_container_width=True)

st.success("💎 High CLV customers should be targeted with premium offers.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 📈 2. REVENUE TREND (FINAL CLEAN + INDUSTRY LEVEL)
# =========================================================

st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📈 Revenue Trend")

# ================== GRANULARITY CONTROL ==================
granularity = st.radio(
    "Select Time View",
    ["Daily", "Weekly", "Monthly"],
    horizontal=True
)

# ================== DATA PREPARATION ==================
if granularity == "Daily":
    time_df = df.groupby(df['Order_date'].dt.date)['Total_Spend'].sum().reset_index()

elif granularity == "Weekly":
    time_df = df.groupby(df['Order_date'].dt.to_period('W'))['Total_Spend'].sum().reset_index()
    time_df['Order_date'] = time_df['Order_date'].astype(str)

else:  # Monthly
    time_df = df.groupby(df['Order_date'].dt.to_period('M'))['Total_Spend'].sum().reset_index()
    time_df['Order_date'] = time_df['Order_date'].astype(str)

# ✅ Sort data (VERY IMPORTANT)
time_df = time_df.sort_values(by='Order_date')

# ================== SMOOTHING ==================
window = 7 if granularity == "Daily" else 3
time_df['Smooth'] = time_df['Total_Spend'].rolling(window).mean()

# ================== PLOT ==================
fig = go.Figure()

# Actual (background line)
fig.add_trace(go.Scatter(
    x=time_df['Order_date'],
    y=time_df['Total_Spend'],
    mode='lines',
    name='Actual',
    line=dict(color='gray', width=1),
    opacity=0.25
))

# Smooth line (main focus)
fig.add_trace(go.Scatter(
    x=time_df['Order_date'],
    y=time_df['Smooth'],
    mode='lines',
    name=f'{window}-Period Avg',
    line=dict(color='#22c55e', width=3)
))

# ================== PEAK DETECTION ==================
valid_df = time_df.dropna()

if not valid_df.empty:
    peak_idx = valid_df['Smooth'].idxmax()

    fig.add_annotation(
        x=valid_df.loc[peak_idx, 'Order_date'],
        y=valid_df.loc[peak_idx, 'Smooth'],
        text="📌 Peak",
        showarrow=True,
        arrowhead=2,
        yshift=20
    )

# ================== LAYOUT ==================
fig.update_layout(
    title="Revenue Trend with Moving Average",
    xaxis_title="Date",
    yaxis_title="Revenue (₹)",
    yaxis_tickprefix="₹",
    hovermode="x unified",
    margin=dict(t=60, b=40)
)

# Better hover
fig.update_traces(
    hovertemplate="<b>Date:</b> %{x}<br><b>Revenue:</b> ₹%{y:,.0f}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

# ================== SMART INSIGHT ==================
if not valid_df.empty:
    peak_value = valid_df['Smooth'].max()

    st.success(
        f"📈 Revenue shows a clear peak (~₹{peak_value:,.0f}). "
        f"Analyze campaigns, festivals, or seasonal demand."
    )
else:
    st.warning("Not enough data to compute trend.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 📦 CATEGORY PERFORMANCE (NEW)
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📦 Category-wise Revenue")

cat_df = df.groupby('Product_Category')['Total_Spend'].sum().reset_index()
cat_df = cat_df.sort_values(by='Total_Spend', ascending=False)

fig = px.bar(
    cat_df,
    x='Product_Category',
    y='Total_Spend',
    color='Product_Category',
    text='Total_Spend'
)

fig.update_traces(
    texttemplate='₹%{text:,.0f}',
    textposition='outside'
)

st.plotly_chart(fig, use_container_width=True)

top_cat = cat_df.iloc[0]
st.info(f"📦 '{top_cat['Product_Category']}' generates highest revenue.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 🌆 CITY PERFORMANCE (NEW)
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("🌆 City-wise Revenue")

city_df = df.groupby('City')['Total_Spend'].sum().reset_index()
city_df = city_df.sort_values(by='Total_Spend', ascending=False)

fig = px.bar(
    city_df,
    x='City',
    y='Total_Spend',
    color='City',
    text='Total_Spend'
)

fig.update_traces(
    texttemplate='₹%{text:,.0f}',
    textposition='outside'
)

st.plotly_chart(fig, use_container_width=True)

top_city = city_df.iloc[0]
st.info(f"🌆 '{top_city['City']}' is the top performing city.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 📊 FREQUENCY DISTRIBUTION (NEW)
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("📊 Customer Frequency Distribution")

freq_df = rfm['Frequency'].value_counts().reset_index()
freq_df.columns = ['Frequency', 'Customers']
freq_df = freq_df.sort_values(by='Frequency')

fig = px.bar(
    freq_df,
    x='Frequency',
    y='Customers',
    text='Customers',
    color='Frequency'
)

fig.update_traces(textposition='outside')

st.plotly_chart(fig, use_container_width=True)

top_freq = freq_df.iloc[0]['Frequency']
st.warning(f"👥 Most customers are at frequency level {top_freq} — low engagement group.")

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 💡 CUSTOMER BEHAVIOR (FINAL CORRECT VERSION)
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("💡 Customer Behavior Analysis")

import numpy as np

# -----------------------------
# SAFE SAMPLING
# -----------------------------
if len(rfm) > 0:
    sample = rfm.sample(min(1500, len(rfm)), random_state=42).copy()
else:
    sample = rfm.copy()

# -----------------------------
# ADD JITTER (fix stacking)
# -----------------------------
sample['Frequency_jitter'] = sample['Frequency'] + np.random.uniform(-0.05, 0.05, len(sample))

# -----------------------------
# SCATTER PLOT
# -----------------------------
fig = px.scatter(
    sample,
    x='Frequency_jitter',
    y='Monetary',
    color='Segment',
    opacity=0.5,
    color_discrete_map={
        'At Risk': '#22c55e',
        'Recent': '#f97316',
        'Loyal': '#3b82f6',
        'Champions': '#eab308'
    }
)

# Marker styling
fig.update_traces(
    marker=dict(size=6),
    selector=dict(mode='markers')
)

# -----------------------------
# GLOBAL TRENDLINE (NEUTRAL)
# -----------------------------
trend = px.scatter(sample, x='Frequency', y='Monetary', trendline="ols")
fig.add_traces(trend.data[1:])

fig.data[-1].line.color = "#60a5fa"   # neutral blue
fig.data[-1].line.width = 3

# -----------------------------
# LAYOUT
# -----------------------------
fig.update_layout(
    xaxis_title="Purchase Frequency",
    yaxis_title="Customer Spending (₹)",
    yaxis_tickprefix="₹",
    legend_title_text="Segment"
)

# Hover
fig.update_traces(
    hovertemplate="Frequency: %{x:.2f}<br>Spend: ₹%{y:,.0f}"
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# SMART INSIGHTS (FIXED + SAFE)
# -----------------------------
if len(rfm) > 1:

    # Correlation
    corr = rfm['Frequency'].corr(rfm['Monetary'])

    if corr > 0.6:
        relation = "strong"
    elif corr > 0.3:
        relation = "moderate"
    else:
        relation = "weak"

    # Segment spend (SAFE + VALIDATED)
    segment_spend = rfm.groupby('Segment')['Monetary'].mean().sort_values(ascending=False)
    top_segment = segment_spend.index[0]
    top_value = segment_spend.iloc[0]

    # Best frequency (ensure exists in current data)
    freq_spend = rfm.groupby('Frequency')['Monetary'].mean()
    top_freq = freq_spend.idxmax()

    # Safety check (IMPORTANT FIX)
    valid_freqs = sample['Frequency'].unique()
    if top_freq not in valid_freqs:
        top_freq = int(max(valid_freqs))

    # Most common frequency (density)
    most_common_freq = int(rfm['Frequency'].mode()[0])

    # -----------------------------
    # DISPLAY INSIGHTS
    # -----------------------------
    st.info(
f"""
📊 There is a **{relation} relationship** between purchase frequency and spending.

💰 '{top_segment}' customers generate the highest average revenue (₹{top_value:,.0f}).

📈 Peak spending occurs around frequency level {top_freq}.

👥 Most customers are concentrated at frequency level {most_common_freq} (low engagement users).

🎯 High-value customers are mainly observed in frequency range 4–6.
"""
)

st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# 💳 PAYMENT DISTRIBUTION (FINAL PRODUCTION VERSION)
# =========================================================
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.subheader("💳 Payment Distribution")

# -----------------------------
# FILTERED DATA (USE SAME FILTERS)
# -----------------------------
filtered_df = df[
    (df['City'].isin(city)) &
    (df['Product_Category'].isin(category))
]

# -----------------------------
# DATA PREPARATION
# -----------------------------
pay_df = filtered_df['Payment_Method'].value_counts(normalize=True).reset_index()
pay_df.columns = ['Payment_Method', 'Percentage']

# Remove very small categories (<1%)
pay_df = pay_df[pay_df['Percentage'] > 0.01]

# Sort descending
pay_df = pay_df.sort_values(by='Percentage', ascending=False)

# -----------------------------
# DONUT CHART
# -----------------------------
fig = px.pie(
    pay_df,
    names='Payment_Method',
    values='Percentage',
    hole=0.6,
    color='Payment_Method',
    color_discrete_map={
        'UPI': '#60a5fa',
        'Credit Card': '#3b82f6',
        'Debit Card': '#f97316',
        'Cash on Delivery': '#ef4444',
        'Wallet': '#22c55e'
    }
)

# Highlight top method
pull_values = [0.08 if i == 0 else 0 for i in range(len(pay_df))]

fig.update_traces(
    textposition='outside',
    textinfo='percent',
    pull=pull_values
)

fig.update_layout(
    legend_title="Payment Type",
    margin=dict(t=20, b=20, l=20, r=20)
)

# Center label
fig.add_annotation(
    text="Payments",
    x=0.5, y=0.5,
    showarrow=False,
    font_size=16
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# INSIGHTS (FINAL POLISHED)
# -----------------------------
if len(pay_df) > 0:

    top_payment = pay_df.iloc[0]['Payment_Method']
    top_value = pay_df.iloc[0]['Percentage'] * 100

    # Digital share (UPI + Cards)
    digital_methods = ['UPI', 'Credit Card', 'Debit Card']
    digital_share = pay_df[
        pay_df['Payment_Method'].isin(digital_methods)
    ]['Percentage'].sum() * 100

    # COD share
    cod_share = pay_df[
        pay_df['Payment_Method'] == 'Cash on Delivery'
    ]['Percentage'].sum() * 100

    st.info(
f"""
💳 Most preferred payment method is **{top_payment}** ({top_value:.1f}%).

📱 Digital payments dominate with **{digital_share:.1f}% share**.

📉 Cash on Delivery remains low at **{cod_share:.1f}%**.

📊 Trend Insight: Customers are shifting towards faster digital payment methods.

💡 Business Insight: Promote Wallet/COD offers to balance payment mix.
"""
)

st.markdown("</div>", unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
ist = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; background-color: #fafafa10; border-radius: 8px;'>
    🛒 <b style='color: #aaa;'>Smart Quick Commerce</b> &nbsp;|&nbsp; Customer Behavior Analysis Dashboard &nbsp;|&nbsp; Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b style='color: #bbb;'>{now}</b></i><br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter customer engagement decisions.</span>
</div>
""", unsafe_allow_html=True)