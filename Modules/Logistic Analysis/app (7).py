import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib as mpl
import numpy as np
import datetime
import pytz

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Logistics Analysis Dashboard",
    page_icon="📦",
    layout="centered",
)

# ── Global Matplotlib style ───────────────────────────────────────────────────
mpl.rcParams.update({
    "figure.facecolor":  "none",
    "axes.facecolor":    "#1c1c2e",
    "axes.edgecolor":    "#3a3a5a",
    "axes.labelcolor":   "#c8c8d0",
    "axes.titlesize":    12,
    "axes.titleweight":  "bold",
    "axes.titlecolor":   "#ffffff",
    "axes.grid":         True,
    "grid.color":        "#2e2e4e",
    "grid.linestyle":    "--",
    "grid.alpha":        0.6,
    "xtick.color":       "#a0a0b0",
    "ytick.color":       "#a0a0b0",
    "xtick.labelsize":   9,
    "ytick.labelsize":   9,
    "text.color":        "#c8c8d0",
    "legend.facecolor":  "#1c1c2e",
    "legend.edgecolor":  "#3a3a5a",
    "legend.fontsize":   8,
    "font.family":       "DejaVu Sans",
})

PALETTE = ["#4f6ef7","#f7a94f","#4ff7c8","#f74f82","#a4f74f","#c47ff7","#f7e24f","#4fc8f7"]
BLUE    = "#4f6ef7"

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
    background-color: #0e0e0e !important;
    color: #e0e0e0 !important;
}
.block-container { padding: 2rem 2rem 2rem 2rem; max-width: 960px; }

.metric-card {
    background: #1c1c2e;
    border-radius: 10px;
    padding: 16px 12px;
    text-align: center;
    border-left: 4px solid #4f6ef7;
    margin-bottom: 8px;
}
.metric-val   { font-size: 24px; font-weight: 700; color: #ffffff; }
.metric-label { font-size: 12px; color: #a0a0b0; margin-top: 4px; }

div[data-testid="stSelectbox"] > div > div {
    background-color: #1c1c2e !important;
    border: 1px solid #3a3a5a !important;
    border-radius: 6px !important;
    color: #e0e0e0 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("QCFE9_Perfect_Discount_Statergy.csv")
    df["Order_date"] = pd.to_datetime(df["Order_date"], errors="coerce")
    df["Month_Name"] = df["Order_date"].dt.strftime("%b %Y")
    return df

df = load_data()

# ── TITLE + SUBTITLE + OBJECTIVE ─────────────────────────────────────────────
st.markdown("<h2 style='text-align: center; color: white;'> Smart Quick Commerce</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: orange;'>📦 Logistics Analysis Dashboard</h1>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style='padding: 16px 20px; border-left: 5px solid #4b6bfb; border-radius: 8px; margin-bottom: 20px; color: #c8c8d0;'>
    <b style='color: white;'>🎯 Objective</b><br><br>
    The objective is to analyze logistics performance across cities, companies, and product categories
    in the quick commerce space. It helps businesses monitor delivery efficiency, customer satisfaction,
    payment patterns, and discount strategies. 
</div>
""", unsafe_allow_html=True)

# ── Inline filters (sidebar removed) ─────────────────────────────────────────
col_f1, col_f2 = st.columns(2)
with col_f1:
    cities    = ["All"] + sorted(df["City"].dropna().unique().tolist())
    sel_city  = st.selectbox("🏙️ Select City", cities)
with col_f2:
    companies  = ["All"] + sorted(df["Company"].dropna().unique().tolist())
    sel_company = st.selectbox("🏢 Select Company", companies)

# ── Apply filters ─────────────────────────────────────────────────────────────
filtered = df.copy()
if sel_city    != "All": filtered = filtered[filtered["City"]    == sel_city]
if sel_company != "All": filtered = filtered[filtered["Company"] == sel_company]

city_label = sel_city    if sel_city    != "All" else "All Cities"
comp_label = sel_company if sel_company != "All" else "All Companies"
st.caption(f"Showing data for **{city_label}** · **{comp_label}** — {len(filtered):,} orders")

st.markdown("---")

# ── KPI row ───────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)

def kpi_card(col, label, value):
    col.markdown(
        f"<div class='metric-card'>"
        f"<div class='metric-val'>{value}</div>"
        f"<div class='metric-label'>{label}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

kpi_card(k1, "Total Orders",          f"{len(filtered):,}")
kpi_card(k2, "Avg Order Value (₹)",   f"₹{filtered['Order_Value'].mean():,.0f}")
kpi_card(k3, "Avg Delivery (min)",    f"{filtered['Delivery_Time_Minute'].mean():.1f}")
kpi_card(k4, "Avg Customer Rating",   f"{filtered['Customer_Rating'].mean():.2f} ⭐")
kpi_card(k5, "Avg Discount Applied",  f"{filtered['Discount_Applied'].mean():.1f}%")

st.markdown("---")

# ── Helper ────────────────────────────────────────────────────────────────────
def make_fig(h=4):
    fig, ax = plt.subplots(figsize=(6, h))
    fig.patch.set_alpha(0)
    return fig, ax

def finalize(fig):
    plt.tight_layout()
    st.pyplot(fig, transparent=True)
    plt.close()

# ── Row 1: Orders by Company | Payment Methods ───────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.subheader("📊 Orders by Company")
    comp_counts = filtered["Company"].value_counts().reset_index()
    comp_counts.columns = ["Company", "Orders"]
    fig, ax = make_fig()
    bars = ax.barh(comp_counts["Company"], comp_counts["Orders"],
                   color=PALETTE[:len(comp_counts)], height=0.6)
    ax.bar_label(bars, labels=[f"{v:,}" for v in comp_counts["Orders"]],
                 padding=5, fontsize=8, color="#c8c8d0")
    ax.set_xlabel("Orders")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_title("Order volume per company")
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    finalize(fig)

with c2:
    st.subheader("💳 Payment Methods")
    pay = filtered["Payment_Method"].value_counts()
    fig, ax = make_fig()
    wedges, texts, autotexts = ax.pie(
        pay.values, labels=pay.index, autopct="%1.1f%%",
        startangle=140, colors=PALETTE[:len(pay)],
        wedgeprops=dict(linewidth=1.5, edgecolor="#0e0e0e"),
        pctdistance=0.82,
    )
    for t in texts:     t.set_color("#c8c8d0"); t.set_fontsize(9)
    for t in autotexts: t.set_color("#ffffff"); t.set_fontsize(8); t.set_fontweight("bold")
    ax.set_title("Payment method split")
    finalize(fig)

# ── Row 2: Delivery Time | Rating Distribution ────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    st.subheader("🚚 Avg Delivery Time by Company")
    del_time = (filtered.groupby("Company")["Delivery_Time_Minute"]
                .mean().sort_values(ascending=False).reset_index())
    fig, ax = make_fig()
    bars = ax.bar(del_time["Company"], del_time["Delivery_Time_Minute"],
                  color=PALETTE[:len(del_time)], width=0.55)
    ax.set_ylabel("Minutes")
    ax.set_xticklabels(del_time["Company"], rotation=35, ha="right", fontsize=8)
    for bar, val in zip(ax.patches, del_time["Delivery_Time_Minute"]):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                f"{val:.1f}", ha="center", va="bottom", fontsize=8, color="#ffffff")
    ax.set_title("Average delivery time (min) per company")
    ax.grid(axis="x", visible=False)
    finalize(fig)

with c4:
    st.subheader("⭐ Customer Rating Distribution")
    fig, ax = make_fig()
    ax.hist(filtered["Customer_Rating"].dropna(), bins=10,
            color=BLUE, edgecolor="#0e0e0e", alpha=0.9, linewidth=0.8)
    ax.set_xlabel("Rating")
    ax.set_ylabel("Orders")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_title("Distribution of customer ratings")
    finalize(fig)

# ── Row 3: Product Category | Customer Type ───────────────────────────────────
c5, c6 = st.columns(2)

with c5:
    st.subheader("🛒 Orders by Product Category")
    cat_data = filtered["Product_Category"].value_counts().reset_index()
    cat_data.columns = ["Category", "Orders"]
    fig, ax = make_fig()
    bars = ax.barh(cat_data["Category"], cat_data["Orders"],
                   color=PALETTE[:len(cat_data)], height=0.55)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.bar_label(bars, labels=[f"{v:,}" for v in cat_data["Orders"]],
                 padding=5, fontsize=8, color="#c8c8d0")
    ax.set_title("Top product categories")
    ax.grid(axis="x"); ax.grid(axis="y", visible=False)
    finalize(fig)

with c6:
    st.subheader("👤 Customer Type Breakdown")
    ctype = filtered["Customer_Type"].value_counts()
    fig, ax = make_fig()
    wedges, texts, autotexts = ax.pie(
        ctype.values, labels=ctype.index, autopct="%1.1f%%",
        startangle=90, colors=PALETTE[:len(ctype)],
        wedgeprops=dict(linewidth=1.5, edgecolor="#0e0e0e"),
        pctdistance=0.82,
    )
    for t in texts:     t.set_color("#c8c8d0"); t.set_fontsize(9)
    for t in autotexts: t.set_color("#ffffff"); t.set_fontsize(8); t.set_fontweight("bold")
    ax.set_title("Customer segments")
    finalize(fig)

# ── Row 4: Discount vs Order Value scatter ────────────────────────────────────
st.subheader("💰 Discount Applied vs Order Value")
sample = filtered[["Discount_Applied", "Order_Value", "Company"]].dropna().sample(
    min(3000, len(filtered)), random_state=42
)
companies_in = sample["Company"].unique()
color_map = {c: PALETTE[i % len(PALETTE)] for i, c in enumerate(companies_in)}

fig, ax = plt.subplots(figsize=(10, 4))
fig.patch.set_alpha(0)
for comp, grp in sample.groupby("Company"):
    ax.scatter(grp["Discount_Applied"], grp["Order_Value"],
               label=comp, alpha=0.5, s=14, color=color_map[comp])
ax.set_xlabel("Discount Applied (%)")
ax.set_ylabel("Order Value (₹)")
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"₹{int(x):,}"))
ax.legend(fontsize=8, ncol=4, loc="upper right",
          facecolor="#1c1c2e", edgecolor="#3a3a5a", labelcolor="#c8c8d0")
ax.set_title("Relationship between discount and order value  (sample of 3,000 orders)")
plt.tight_layout()
st.pyplot(fig, transparent=True)
plt.close()

# ── Footer ────────────────────────────────────────────────────────────────────
ist = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; background-color: #fafafa10; border-radius: 8px;'>
    🛒 <b style='color: #aaa;'>Smart Quick Commerce</b> &nbsp;|&nbsp; Logistics Analysis Dashboard &nbsp;|&nbsp; Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b style='color: #bbb;'>{now}</b></i><br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter logistics and delivery decisions.</span>
</div>
""", unsafe_allow_html=True)