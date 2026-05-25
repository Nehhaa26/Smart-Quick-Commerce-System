# 🛒 Smart Quick Commerce Intelligence System

> A machine learning and analytics-based platform to improve decision-making in quick commerce operations — developed during internship at **Stark Technologies**.

---

## 📌 Project Overview

The **Smart Quick Commerce Intelligence System** is a centralized, AI-powered dashboard built with **Streamlit** that integrates multiple analytical and predictive modules to optimize quick commerce operations. From demand forecasting to sentiment analysis, the system enables data-driven decisions across the entire commerce pipeline.

This project was developed by **Patel Neha Arvindbhai** as part of the B.E. Computer Engineering internship program at **S.P.B. Patel Engineering College, Mehsana** (Gujarat Technological University), in collaboration with Stark Technologies.

---

## 🚀 Modules

| Module | Description |
|---|---|
| 📈 **Demand Forecasting** | Predicts future product demand using time-series and ML models |
| 📦 **Inventory Optimization** | Minimizes stockouts and overstock using demand signals |
| 🛍️ **Recommendation System** | Suggests relevant products to customers |
| 🚚 **Delivery Performance Prediction** | Predicts delivery time and efficiency |
| 👥 **Customer Segmentation** | Groups customers using RFM analysis and clustering |
| 🔍 **Customer Behavior Analysis** | Analyzes purchase patterns and customer lifetime value |
| 🗺️ **Logistics Analysis** | Evaluates weather, distance, and routing impact |
| 💬 **Sentiment Analysis** | Processes customer reviews to extract sentiment and issue types |

---

## 🧠 Machine Learning Algorithms Used

- **XGBoost** — demand and delivery prediction
- **Random Forest** — classification and regression tasks
- **K-Means Clustering** — customer segmentation
- **Gaussian Mixture Model (GMM)** — probabilistic customer grouping
- **TextBlob & VADER** — NLP-based sentiment scoring

---

## 🛠️ Tech Stack

| Category | Tools / Libraries |
|---|---|
| Language | Python |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn, XGBoost |
| NLP | TextBlob, VADER |
| Visualization | Matplotlib, Seaborn, Plotly |
| Dashboard | Streamlit |
| Feature Engineering | RFM Analysis, Lag Features, Rolling Statistics |

---

## 📊 Key Features

- **Centralized Streamlit Dashboard** with module selection screen
- **Interactive visualizations** — demand trends, delivery time patterns, customer segments, sentiment distributions
- **End-to-end ML pipeline** — data preprocessing → feature engineering → model training → prediction
- Missing value handling, outlier removal, and data type normalization
- Real-time insights for inventory planning, logistics, and customer engagement

---

## 🗂️ Dataset Tables

| Table | Description |
|---|---|
| `Customer` | Customer demographics and type |
| `Orders` | Main transaction records |
| `Product` | Product catalog and categories |
| `Delivery` | Delivery time, partner rating, city |
| `Review & Sentiment` | Customer reviews and sentiment labels |

---

## 📁 Project Structure

```
smart-quick-commerce/
├── data/                  # Raw and processed datasets
├── notebooks/             # EDA and model experiments
├── modules/
│   ├── demand_forecasting.py
│   ├── inventory_optimization.py
│   ├── recommendation_system.py
│   ├── delivery_performance.py
│   ├── customer_segmentation.py
│   ├── customer_behavior.py
│   ├── logistics_analysis.py
│   └── sentiment_analysis.py
├── dashboard/
│   └── app.py             # Centralized Streamlit UI
├── requirements.txt
└── README.md
```

---

## ⚙️ Getting Started

### Prerequisites

```bash
Python 3.8+
pip
```

### Installation

```bash
# Clone the repository
git clone https://github.com/your-username/smart-quick-commerce.git
cd smart-quick-commerce

# Install dependencies
pip install -r requirements.txt
```

### Run the Dashboard

```bash
streamlit run dashboard/app.py
```

---

## 📋 Requirements

```
pandas
numpy
scikit-learn
xgboost
streamlit
plotly
matplotlib
seaborn
textblob
vaderSentiment
```

---

## 👩‍💻 Author

**Patel Neha Arvindbhai**
B.E. Computer Engineering — 8th Semester
S.P.B. Patel Engineering College, Mehsana
Gujarat Technological University, Ahmedabad

**Internship at:** Stark Technologies
**External Guide:** Mr. Sumit Chawla
**Internal Guide:** Prof. Kunalsinh Kathia

---

## 🙏 Acknowledgements

Special thanks to **Stark Technologies** and supervisor **Mr. Sumit Chawla** for mentorship and industry exposure, and to **Prof. Kunalsinh Kathia** and **HOD Prof. Akshay Kansara** at S.P.B. Patel Engineering College for their academic guidance.

---

## 📄 License

This project was developed for academic and internship purposes. All rights reserved © 2026 Patel Neha Arvindbhai.
