import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import datetime
import pytz

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QCommerce Sentiment Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 1rem; }
    .metric-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        border-left: 4px solid #4CAF50;
    }
    h1 { font-size: 1.6rem !important; }
    .stTabs [data-baseweb="tab"] { font-size: 0.9rem; font-weight: 500; }
    div[data-testid="metric-container"] {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        border: 1px solid #e9ecef;
    }
</style>
""", unsafe_allow_html=True)

# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df["Order_date"] = pd.to_datetime(df["Order_date"])
    df["Sentiment_Label"] = df["Sentiment_Label"].str.strip()
    df["Issue_Type"] = df["Issue_Type"].str.strip()
    df["Company"] = df["Company"].str.strip()
    df["City"] = df["City"].str.strip()
    return df

# ── Adjust this path to your CSV location ─────────────────────────────────────
DATA_PATH = "QCFE9_Perfect_Discount_Statergy.csv"
df = load_data(DATA_PATH)

# ── Color maps ────────────────────────────────────────────────────────────────
SENTIMENT_COLORS = {"Positive": "#4CAF50", "Neutral": "#FFC107", "Negative": "#F44336"}
COMPANY_COLORS = px.colors.qualitative.Set2
CITY_COLORS = px.colors.qualitative.Pastel

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/48/delivery--v1.png", width=48)
    st.title("Filters")
    st.markdown("---")

    companies = ["All"] + sorted(df["Company"].unique().tolist())
    sel_company = st.multiselect("Company", companies, default=["All"])

    cities = ["All"] + sorted(df["City"].unique().tolist())
    sel_city = st.multiselect("City", cities, default=["All"])

    month_map = {8: "August", 9: "September", 10: "October", 11: "November"}
    months = sorted(df["Month"].unique().tolist())
    sel_months = st.multiselect("Month", [month_map[m] for m in months], default=[month_map[m] for m in months])
    sel_month_nums = [k for k, v in month_map.items() if v in sel_months]

    sentiment_options = df["Sentiment_Label"].unique().tolist()
    sel_sentiment = st.multiselect("Sentiment Label", sentiment_options, default=sentiment_options)

    customer_types = df["Customer_Type"].unique().tolist()
    sel_ctype = st.multiselect("Customer Type", customer_types, default=customer_types)

    st.markdown("---")
    st.caption(f"Dataset: **{len(df):,}** total orders")

# ── Apply filters ─────────────────────────────────────────────────────────────
dff = df.copy()
if "All" not in sel_company and sel_company:
    dff = dff[dff["Company"].isin(sel_company)]
if "All" not in sel_city and sel_city:
    dff = dff[dff["City"].isin(sel_city)]
if sel_month_nums:
    dff = dff[dff["Month"].isin(sel_month_nums)]
if sel_sentiment:
    dff = dff[dff["Sentiment_Label"].isin(sel_sentiment)]
if sel_ctype:
    dff = dff[dff["Customer_Type"].isin(sel_ctype)]

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("<h2 style='text-align: center; color: white;'> Smart Quick Commerce</h2>", unsafe_allow_html=True)
st.markdown("<h1 style='text-align: center; color: orange;'>📊 Customer Sentiment Analysis</h1>", unsafe_allow_html=True)

st.markdown("---")

st.markdown("""
<div style='padding: 16px 20px; border-left: 5px solid #4b6bfb; border-radius: 8px; margin-bottom: 20px; color: #c8c8d0;'>
    <b style='color: white;'>🎯 Objective</b><br><br>
    The objective is to analyze customer sentiment across orders, cities, companies, and product categories
    in the quick commerce space. It helps businesses identify pain points, track delivery impact on customer
    experience, and monitor issue trends. This enables data-driven decisions to improve service quality,
    reduce negative feedback, and enhance overall customer satisfaction.
</div>
""", unsafe_allow_html=True)

st.caption(f"Showing **{len(dff):,}** orders after filters · Months: Aug–Nov 2025 · 8 companies · 12 cities")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",
    "🏙️ City Analysis",
    "🏢 Company Analysis",
    "🚚 Delivery Impact",
    "🔍 Issue Tracker",
])

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    total = len(dff)
    pos = (dff["Sentiment_Label"] == "Positive").sum()
    neu = (dff["Sentiment_Label"] == "Neutral").sum()
    neg = (dff["Sentiment_Label"] == "Negative").sum()
    avg_score = dff["Sentiment_Score"].mean()
    delay_rate = dff["Delay_Flag"].mean() * 100

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    c1.metric("Total Orders", f"{total:,}")
    c2.metric("Avg Sentiment Score", f"{avg_score:.3f}")
    c3.metric("Positive", f"{pos/total*100:.1f}%", f"{pos:,}")
    c4.metric("Neutral", f"{neu/total*100:.1f}%", f"{neu:,}")
    c5.metric("Negative", f"{neg/total*100:.1f}%", f"{neg:,}", delta_color="inverse")
    c6.metric("Delay Rate", f"{delay_rate:.1f}%", delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns([1, 2])

    with col1:
        st.subheader("Sentiment Distribution")
        sent_counts = dff["Sentiment_Label"].value_counts().reset_index()
        sent_counts.columns = ["Sentiment", "Count"]
        fig_donut = px.pie(
            sent_counts, names="Sentiment", values="Count",
            hole=0.55, color="Sentiment",
            color_discrete_map=SENTIMENT_COLORS,
        )
        fig_donut.update_traces(textposition="outside", textinfo="percent+label")
        fig_donut.update_layout(showlegend=False, margin=dict(t=10, b=10, l=10, r=10), height=320)
        st.plotly_chart(fig_donut, use_container_width=True)

    with col2:
        st.subheader("Sentiment Score Trend by Month")
        month_trend = dff.groupby("Month").agg(
            Avg_Score=("Sentiment_Score", "mean"),
            Positive=("Sentiment_Label", lambda x: (x == "Positive").sum()),
            Negative=("Sentiment_Label", lambda x: (x == "Negative").sum()),
        ).reset_index()
        month_trend["Month_Name"] = month_trend["Month"].map(month_map)

        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=month_trend["Month_Name"], y=month_trend["Avg_Score"],
            mode="lines+markers+text", name="Avg Score",
            line=dict(color="#378ADD", width=3),
            marker=dict(size=10),
            text=month_trend["Avg_Score"].round(3),
            textposition="top center",
            
        ))
        fig_trend.update_layout(
            height=320, margin=dict(t=20, b=20, l=20, r=20),
            yaxis_title="Avg Sentiment Score",
            plot_bgcolor="white",
            yaxis=dict(gridcolor="#f0f0f0"),
        )
        
        fig_trend.update_traces(textfont=dict(color="black"))
        st.plotly_chart(fig_trend, use_container_width=True)

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Sentiment by Product Category")
        cat_sent = dff.groupby(["Product_Category", "Sentiment_Label"]).size().reset_index(name="Count")
        fig_cat = px.bar(
            cat_sent, x="Product_Category", y="Count", color="Sentiment_Label",
            barmode="stack", color_discrete_map=SENTIMENT_COLORS,
        )
        fig_cat.update_layout(height=340, margin=dict(t=10, b=10), plot_bgcolor="white",
                               xaxis_tickangle=-30, legend_title="Sentiment")
        st.plotly_chart(fig_cat, use_container_width=True)

    with col4:
        st.subheader("Sentiment by Customer Type")
        ctype_sent = dff.groupby(["Customer_Type", "Sentiment_Label"]).size().reset_index(name="Count")
        fig_ctype = px.bar(
            ctype_sent, x="Customer_Type", y="Count", color="Sentiment_Label",
            barmode="group", color_discrete_map=SENTIMENT_COLORS,
        )
        fig_ctype.update_layout(height=340, margin=dict(t=10, b=10), plot_bgcolor="white",
                                 legend_title="Sentiment")
        st.plotly_chart(fig_ctype, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2 — CITY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader("City-wise Sentiment Overview")

    city_stats = dff.groupby("City").agg(
        Avg_Score=("Sentiment_Score", "mean"),
        Total_Orders=("Order_ID", "count"),
        Positive=("Sentiment_Label", lambda x: (x == "Positive").sum()),
        Negative=("Sentiment_Label", lambda x: (x == "Negative").sum()),
        Neg_Rate=("Sentiment_Label", lambda x: round((x == "Negative").mean() * 100, 1)),
        Avg_Delivery=("Delivery_Time_Minute", "mean"),
        Delay_Rate=("Delay_Flag", lambda x: round(x.mean() * 100, 1)),
    ).reset_index().sort_values("Avg_Score", ascending=False)

    
    col1, col2 = st.columns(2)

    with col1:
        fig_city_score = px.bar(
            city_stats.sort_values("Avg_Score"),
            x="Avg_Score", y="City", orientation="h",
            color="Avg_Score", color_continuous_scale="RdYlGn",
            title="Average Sentiment Score by City",
            text=city_stats.sort_values("Avg_Score")["Avg_Score"].round(3),
        )
        fig_city_score.update_traces(textposition="outside", textfont=dict(color="black"))
        fig_city_score.update_layout(height=420, margin=dict(t=40, b=10), coloraxis_showscale=False,
                                      plot_bgcolor="white")
        st.plotly_chart(fig_city_score, use_container_width=True)
        

    with col2:
        fig_city_neg = px.bar(
            city_stats.sort_values("Neg_Rate", ascending=False),
            x="City", y="Neg_Rate",
            color="Neg_Rate", color_continuous_scale="Reds",
            title="Negative Sentiment Rate (%) by City",
            text=city_stats.sort_values("Neg_Rate", ascending=False)["Neg_Rate"],
        )
        fig_city_neg.update_traces(textposition="outside", texttemplate="%{text}%",textfont=dict(color="black"))
        fig_city_neg.update_layout(height=420, margin=dict(t=40, b=10), coloraxis_showscale=False,
                                    plot_bgcolor="white", xaxis_tickangle=-30)
        st.plotly_chart(fig_city_neg, use_container_width=True)
       

    st.subheader("City Sentiment vs Delivery Time")
    fig_scatter = px.scatter(
        city_stats, x="Avg_Delivery", y="Avg_Score",
        size="Total_Orders", color="Neg_Rate",
        color_continuous_scale="RdYlGn_r",
        hover_name="City", text="City",
        labels={"Avg_Delivery": "Avg Delivery Time (min)", "Avg_Score": "Avg Sentiment Score"},
        title="City: Delivery Time vs Sentiment Score (bubble = order volume, color = neg rate)",
    )
    fig_scatter.update_traces(textposition="top center", textfont=dict(color="black"))
    fig_scatter.update_layout(height=420, plot_bgcolor="white", margin=dict(t=50, b=20))
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("City Summary Table")
    city_display = city_stats[["City", "Total_Orders", "Avg_Score", "Neg_Rate", "Avg_Delivery", "Delay_Rate"]].copy()
    city_display.columns = ["City", "Orders", "Avg Sentiment", "Negative %", "Avg Delivery (min)", "Delay Rate %"]
    city_display = city_display.sort_values("Negative %", ascending=False)
    st.dataframe(city_display.style.background_gradient(subset=["Negative %"], cmap="Reds")
                                    .background_gradient(subset=["Avg Sentiment"], cmap="Greens")
                                    .format({"Avg Sentiment": "{:.3f}", "Avg Delivery (min)": "{:.1f}"}),
                 use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3 — COMPANY ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader("Company-wise Sentiment Performance")

    co_stats = dff.groupby("Company").agg(
        Avg_Score=("Sentiment_Score", "mean"),
        Total_Orders=("Order_ID", "count"),
        Positive_Pct=("Sentiment_Label", lambda x: round((x == "Positive").mean() * 100, 1)),
        Negative_Pct=("Sentiment_Label", lambda x: round((x == "Negative").mean() * 100, 1)),
        Neutral_Pct=("Sentiment_Label", lambda x: round((x == "Neutral").mean() * 100, 1)),
        Avg_Rating=("Customer_Rating", "mean"),
        Avg_Delivery=("Delivery_Time_Minute", "mean"),
        Delay_Rate=("Delay_Flag", lambda x: round(x.mean() * 100, 1)),
    ).reset_index().sort_values("Avg_Score", ascending=False)

    # Risk tagging
    def risk_tag(score):
        if score >= 0.20: return "🟢 Low Risk"
        elif score >= 0.15: return "🟡 Medium Risk"
        else: return "🔴 High Risk"
    co_stats["Risk"] = co_stats["Avg_Score"].apply(risk_tag)

    col1, col2 = st.columns(2)
    with col1:
        fig_co = px.bar(
            co_stats.sort_values("Avg_Score"),
            x="Avg_Score", y="Company", orientation="h",
            color="Avg_Score", color_continuous_scale="RdYlGn",
            title="Average Sentiment Score by Company",
            text=co_stats.sort_values("Avg_Score")["Avg_Score"].round(3),
        )
        fig_co.update_traces(textposition="outside",textfont=dict(color="black"))
        fig_co.update_layout(height=380, coloraxis_showscale=False, plot_bgcolor="white",
                              margin=dict(t=40, b=10))
        st.plotly_chart(fig_co, use_container_width=True)

    with col2:
        co_melt = co_stats[["Company", "Positive_Pct", "Neutral_Pct", "Negative_Pct"]].melt(
            id_vars="Company", var_name="Sentiment", value_name="Pct"
        )
        co_melt["Sentiment"] = co_melt["Sentiment"].str.replace("_Pct", "")
        fig_co_stack = px.bar(
            co_melt, x="Company", y="Pct", color="Sentiment",
            color_discrete_map=SENTIMENT_COLORS,
            title="Sentiment Mix per Company (%)",
            barmode="stack",
        )
        fig_co_stack.update_layout(height=380, plot_bgcolor="white", xaxis_tickangle=-30,
                                    margin=dict(t=40, b=10), legend_title="")
        st.plotly_chart(fig_co_stack, use_container_width=True)

    st.subheader("Company Sentiment by Product Category")
    co_cat = dff.groupby(["Company", "Product_Category"])["Sentiment_Score"].mean().reset_index()
    fig_heat = px.density_heatmap(
        co_cat, x="Product_Category", y="Company", z="Sentiment_Score",
        color_continuous_scale="RdYlGn",
        title="Avg Sentiment Score — Company × Product Category",
    )
    fig_heat.update_layout(height=380, margin=dict(t=50, b=10))
    st.plotly_chart(fig_heat, use_container_width=True)

    st.subheader("Company Scorecard")
    co_display = co_stats[["Company", "Risk", "Total_Orders", "Avg_Score", "Positive_Pct",
                             "Negative_Pct", "Avg_Rating", "Avg_Delivery", "Delay_Rate"]].copy()
    co_display.columns = ["Company", "Risk", "Orders", "Avg Sentiment", "Positive %",
                           "Negative %", "Avg Rating", "Avg Delivery (min)", "Delay Rate %"]
    st.dataframe(co_display.style.background_gradient(subset=["Negative %"], cmap="Reds")
                                  .background_gradient(subset=["Avg Sentiment"], cmap="Greens")
                                  .format({"Avg Sentiment": "{:.3f}", "Avg Rating": "{:.2f}",
                                           "Avg Delivery (min)": "{:.1f}"}),
                 use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 4 — DELIVERY IMPACT
# ═══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.subheader("How Delivery Affects Customer Sentiment")

    d1, d2, d3, d4 = st.columns(4)
    d1.metric("Avg Delivery Time", f"{dff['Delivery_Time_Minute'].mean():.1f} min")
    d2.metric("Delayed Orders", f"{dff['Delay_Flag'].sum():,}", f"{dff['Delay_Flag'].mean()*100:.1f}%", delta_color="inverse")
    d3.metric("Avg Partner Rating", f"{dff['Delivery_Partner_Rating'].mean():.2f}")
    d4.metric("Avg Customer Rating", f"{dff['Customer_Rating'].mean():.2f}")

    st.markdown("---")

    # Delivery time buckets
    bins = [0, 15, 25, 35, 45, 100]
    labels = ["0–15 min", "16–25 min", "26–35 min", "36–45 min", "45+ min"]
    dff2 = dff.copy()
    dff2["Delivery_Bucket"] = pd.cut(dff2["Delivery_Time_Minute"], bins=bins, labels=labels)
    bucket_sent = dff2.groupby("Delivery_Bucket", observed=True).agg(
        Avg_Score=("Sentiment_Score", "mean"),
        Neg_Rate=("Sentiment_Label", lambda x: round((x == "Negative").mean() * 100, 1)),
        Count=("Order_ID", "count"),
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig_bucket = px.bar(
            bucket_sent, x="Delivery_Bucket", y="Avg_Score",
            color="Avg_Score", color_continuous_scale="RdYlGn",
            title="Avg Sentiment Score by Delivery Time Bucket",
            text=bucket_sent["Avg_Score"].round(3),
        )
        fig_bucket.update_traces(textposition="outside", textfont=dict(color="black"))
        fig_bucket.update_layout(height=380, coloraxis_showscale=False, plot_bgcolor="white",
                                  margin=dict(t=50, b=10), xaxis_title="Delivery Time")
        st.plotly_chart(fig_bucket, use_container_width=True)

    with col2:
        # Partner rating buckets
        dff2["Rating_Bucket"] = pd.cut(dff2["Delivery_Partner_Rating"],
                                        bins=[0, 2.5, 3.5, 4.5, 5.1],
                                        labels=["< 2.5", "2.5–3.5", "3.5–4.5", "4.5–5.0"])
        rating_sent = dff2.groupby("Rating_Bucket", observed=True).agg(
            Avg_Score=("Sentiment_Score", "mean"),
        ).reset_index()
        fig_rating = px.bar(
            rating_sent, x="Rating_Bucket", y="Avg_Score",
            color="Avg_Score", color_continuous_scale="RdYlGn",
            title="Avg Sentiment by Delivery Partner Rating",
            text=rating_sent["Avg_Score"].round(3),
        )
        fig_rating.update_traces(textposition="outside",textfont=dict(color="black"))
        fig_rating.update_layout(height=380, coloraxis_showscale=False, plot_bgcolor="white",
                                  margin=dict(t=50, b=10), xaxis_title="Partner Rating")
        st.plotly_chart(fig_rating, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Delayed vs On-Time: Sentiment Comparison")
        delay_sent = dff.groupby(["Delay_Flag", "Sentiment_Label"]).size().reset_index(name="Count")
        delay_sent["Delay_Flag"] = delay_sent["Delay_Flag"].map({0: "On Time", 1: "Delayed"})
        fig_delay = px.bar(
            delay_sent, x="Delay_Flag", y="Count", color="Sentiment_Label",
            barmode="group", color_discrete_map=SENTIMENT_COLORS,
            title="Order Sentiment: Delayed vs On-Time",
        )
        fig_delay.update_layout(height=340, plot_bgcolor="white", margin=dict(t=50, b=10),
                                 legend_title="")
        st.plotly_chart(fig_delay, use_container_width=True)

    with col4:
        st.subheader("Delivery Time Distribution by Sentiment")
        fig_box = px.box(
            dff, x="Sentiment_Label", y="Delivery_Time_Minute",
            color="Sentiment_Label", color_discrete_map=SENTIMENT_COLORS,
            title="Delivery Time Distribution per Sentiment Label",
            points=False,
        )
        fig_box.update_layout(height=340, plot_bgcolor="white", margin=dict(t=50, b=10),
                               showlegend=False, xaxis_title="Sentiment", yaxis_title="Delivery Time (min)")
        st.plotly_chart(fig_box, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 5 — ISSUE TRACKER
# ═══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.subheader("Issue Type Analysis")

    # Exclude 'No Issue' for most charts
    dff_issues = dff[dff["Issue_Type"] != "No Issue"].copy()

    i1, i2, i3 = st.columns(3)
    i1.metric("Orders With Issues", f"{len(dff_issues):,}",
               f"{len(dff_issues)/len(dff)*100:.1f}% of total", delta_color="inverse")
    i2.metric("Top Issue", dff_issues["Issue_Type"].value_counts().index[0])
    i3.metric("Avg Sentiment (Issues)", f"{dff_issues['Sentiment_Score'].mean():.3f}",
               delta_color="inverse")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        issue_counts = dff_issues["Issue_Type"].value_counts().reset_index()
        issue_counts.columns = ["Issue_Type", "Count"]
        fig_issue = px.bar(
            issue_counts.sort_values("Count"),
            x="Count", y="Issue_Type", orientation="h",
            title="Issue Volume (excl. No Issue)",
            text="Count",
        )
        fig_issue.update_traces(textposition="outside")
        fig_issue.update_layout(height=380, coloraxis_showscale=False, plot_bgcolor="white",
                                 margin=dict(t=50, b=10))
        st.plotly_chart(fig_issue, use_container_width=True)

    with col2:
        issue_score = dff_issues.groupby("Issue_Type")["Sentiment_Score"].mean().reset_index()
        issue_score.columns = ["Issue_Type", "Avg_Score"]
        fig_iss_score = px.bar(
            issue_score.sort_values("Avg_Score"),
            x="Avg_Score", y="Issue_Type", orientation="h",
            title="Avg Sentiment Score per Issue Type",
            text=issue_score.sort_values("Avg_Score")["Avg_Score"].round(3),
        )
        fig_iss_score.update_traces(textposition="outside")
        fig_iss_score.update_layout(height=380, coloraxis_showscale=False, plot_bgcolor="white",
                                     margin=dict(t=50, b=10))
        st.plotly_chart(fig_iss_score, use_container_width=True)

    st.subheader("Issue Type by Company")
    co_issue = dff_issues.groupby(["Company", "Issue_Type"]).size().reset_index(name="Count")
    fig_co_issue = px.bar(
        co_issue, x="Company", y="Count", color="Issue_Type",
        barmode="stack", title="Issue Distribution by Company",
    )
    fig_co_issue.update_layout(height=400, plot_bgcolor="white", xaxis_tickangle=-30,
                                margin=dict(t=50, b=10), legend_title="Issue Type")
    st.plotly_chart(fig_co_issue, use_container_width=True)

    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Issue Trend by Month")
        iss_month = dff_issues.groupby(["Month", "Issue_Type"]).size().reset_index(name="Count")
        iss_month["Month_Name"] = iss_month["Month"].map(month_map)
        fig_iss_trend = px.line(
            iss_month, x="Month_Name", y="Count", color="Issue_Type",
            markers=True, title="Monthly Issue Volume Trend",
        )
        fig_iss_trend.update_layout(height=360, plot_bgcolor="white", margin=dict(t=50, b=10),
                                     yaxis=dict(gridcolor="#f0f0f0"), legend_title="Issue")
        st.plotly_chart(fig_iss_trend, use_container_width=True)

    with col4:
        st.subheader("Issue Type by City")
        city_issue = dff_issues.groupby(["City", "Issue_Type"]).size().reset_index(name="Count")
        fig_city_iss = px.bar(
            city_issue, x="City", y="Count", color="Issue_Type",
            barmode="stack", title="Issue Distribution by City",
        )
        fig_city_iss.update_layout(height=360, plot_bgcolor="white", xaxis_tickangle=-30,
                                    margin=dict(t=50, b=10), legend_title="Issue")
        st.plotly_chart(fig_city_iss, use_container_width=True)

    st.subheader("Issue × Sentiment Label Heatmap")
    iss_sent = dff_issues.groupby(["Issue_Type", "Sentiment_Label"]).size().unstack(fill_value=0).reset_index()
    iss_sent_melt = dff_issues.groupby(["Issue_Type", "Sentiment_Label"]).size().reset_index(name="Count")
    fig_iss_heat = px.density_heatmap(
        iss_sent_melt, x="Sentiment_Label", y="Issue_Type", z="Count",
        color_continuous_scale="Oranges",
        title="Issue Type × Sentiment Label Count",
    )
    fig_iss_heat.update_layout(height=350, margin=dict(t=50, b=10))
    st.plotly_chart(fig_iss_heat, use_container_width=True)

    st.markdown("---")
    st.subheader("Raw Issue Records Explorer")
    issue_filter = st.selectbox("Filter by Issue Type", ["All"] + sorted(dff_issues["Issue_Type"].unique().tolist()))
    explorer_df = dff_issues if issue_filter == "All" else dff_issues[dff_issues["Issue_Type"] == issue_filter]
    st.dataframe(
        explorer_df[["Order_ID", "Company", "City", "Customer_Review", "Sentiment_Label",
                      "Sentiment_Score", "Issue_Type", "Delivery_Time_Minute", "Delay_Flag"]]
        .sort_values("Sentiment_Score").head(200),
        use_container_width=True, hide_index=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────────
ist = pytz.timezone("Asia/Kolkata")
now = datetime.datetime.now(ist).strftime("%d %B %Y, %I:%M %p (IST)")

st.markdown("---")
st.markdown(f"""
<div style='text-align: center; padding: 14px; color: #888; font-size: 13px; background-color: #fafafa10; border-radius: 8px;'>
    🛒 <b style='color: #aaa;'>Smart Quick Commerce</b> &nbsp;|&nbsp; Sentiment Intelligence Dashboard &nbsp;|&nbsp; Powered by Machine Learning 🤖 <br><br>
    🕐 <i>Session loaded on: <b style='color: #bbb;'>{now}</b></i><br><br>
    <span style='font-size: 11px;'>© 2026 All rights reserved. Built for smarter customer sentiment decisions.</span>
</div>
""", unsafe_allow_html=True)