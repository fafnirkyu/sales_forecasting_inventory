# 🛒 Sales Forecasting & Inventory Optimization

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-red.svg)](https://streamlit.io/)
[![Power BI](https://img.shields.io/badge/PowerBI-Dashboard-yellow)](powerbi/)
[![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg)](docker/)
[![Kaggle Dataset](https://img.shields.io/badge/Dataset-Kaggle-20BEFF.svg)](https://www.kaggle.com/)  
> End-to-end demand forecasting, inventory optimization, and business insights with **time-series ML, dashboards, and deployable apps**.

---

## 📌 Overview
This project demonstrates a **realistic business pipeline** for a retail store chain:

- **📊 Time-series forecasting** (ARIMA, Prophet, ML models) to predict sales demand.  
- **📦 Inventory optimization**: avoid stockouts and overstock situations.  
- **📈 Power BI Dashboard** for executive-level KPIs.  
- **🌐 Streamlit + FastAPI app** for interactive analysis and simulations.  
- **🐳 Dockerized deployment** for reproducibility and cloud readiness.  

It simulates how data scientists can provide **actionable insights for business decision-making**.

---

## ⚡ Quick Links
- 📂 [Notebooks](notebooks/) — EDA, forecasting, and optimization  
- 🗄️ [Data](data/) — Preprocessed retail dataset (synthetic)  
- 🖥️ [Streamlit App](app/streamlit_app.py) — Interactive dashboard  
- ⚙️ [FastAPI Backend](app/api.py) — REST API for forecasts  
- 📑 [Power BI Reports](powerbi/) — Business KPIs dashboard  
- 🐳 [Docker Setup](docker/) — Containerized deployment  

---

## 📂 Project Structure
```bash
sales_forecasting_inventory/
├── app/                 # Streamlit + FastAPI apps
│   ├── streamlit_app.py
│   └── api.py
├── src/                 # Business logic
│   ├── optimization.py
│   └── utils.py
├── notebooks/           # Jupyter notebooks (EDA, forecasting, optimization)
│   ├── 01_eda.ipynb
│   ├── 02_forecasting.ipynb
│   └── 03_optimization.ipynb
├── data/                # Raw & processed data (from Kaggle)
├── sql/                 # SQL scripts for Power BI integration
├── docker/              # Dockerfile + docker-compose
├── powerbi/             # Power BI dashboard (.pbix)
├── requirements.txt     # Python dependencies
└── README.md
´´´

## 🚀 Deployment
1️⃣ Local (Development)
# Install dependencies
pip install -r requirements.txt

# Run FastAPI backend
uvicorn app.fastapi_app:app --reload --port 8000

# Run Streamlit dashboard
streamlit run app/streamlit_app.py

2️⃣ Docker (Production-ready)
´´´bash
cd docker
docker-compose up --build
´´´

FastAPI → http://localhost:8000

Streamlit → http://localhost:8501

3️⃣ Power BI Integration

Export forecast results to PostgreSQL or CSV.

Connect Power BI to the database for live, refreshable dashboards.

Use included .pbix file in powerbi/
 to explore KPIs.

## 📊 Example Use Cases

Demand Forecasting → Align production with predicted sales.

Inventory Optimization → Minimize costs while avoiding stockouts.

Executive BI Dashboard → Present results with Power BI for decision-makers.

API Integration → Serve forecasts to external systems (ERP, supply chain apps).

## 🧰 Tech Stack

Languages: Python 3.10 (Pandas, Prophet, ARIMA, Scikit-learn)

Apps: Streamlit (UI), FastAPI (API)

BI: Power BI (.pbix reports, SQL integration)

Infra: Docker (multi-service orchestration), PostgreSQL (for persistence)

## 🌟 Why This Project?

This repository showcases end-to-end data science & MLOps skills:

Time-series ML modeling

Business optimization

API + dashboard deployment

Power BI executive reporting

Docker-based productionization

It represents the kind of solution that bridges data science and real business value.