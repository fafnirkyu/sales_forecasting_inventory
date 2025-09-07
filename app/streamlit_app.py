#streamlit run app/streamlit_app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from src.optimization import simulate_reorder

st.set_page_config(page_title="Sales Forecast & Inventory Simulator", layout="wide")

@st.cache_data
def load_data():
    clean = pd.read_csv("data_out/retail_store_inventory_clean.csv", parse_dates=["date"])
    forecast = pd.read_csv("data_out/forecast_prophet.csv", parse_dates=["date"])
    merged = clean.merge(forecast, on=["date","store_id","product_id"], how="left")
    merged["forecast"] = merged["forecast"].fillna(merged.groupby(["store_id","product_id"])["units_sold"].transform(lambda x: x.rolling(7,min_periods=1).mean()))
    return merged

df = load_data()

st.sidebar.title("Controls")
store = st.sidebar.selectbox("Store", sorted(df["store_id"].unique()))
product = st.sidebar.selectbox("Product", sorted(df[df["store_id"]==store]["product_id"].unique()))

lead_time = st.sidebar.number_input("Lead time (days)", min_value=0, max_value=30, value=2)
safety_factor = st.sidebar.slider("Safety stock factor", 1.0, 3.0, 1.2, 0.1)
run_sim = st.sidebar.button("Run simulation")

sku_df = df[(df["store_id"]==store) & (df["product_id"]==product)].sort_values("date")

st.header(f"Store {store} — Product {product}")
st.write("Summary KPIs")
st.write(sku_df[["date","units_sold","inventory_level","forecast"]].describe().transpose())

# Plot actual vs forecast
fig, ax = plt.subplots(figsize=(10,4))
ax.plot(sku_df["date"], sku_df["units_sold"], label="Actual")
ax.plot(sku_df["date"], sku_df["forecast"], label="Forecast", linestyle="--")
ax.set_title("Actual vs Forecast")
ax.legend()
st.pyplot(fig)

if run_sim:
    st.write("Running reorder simulation...")
    sim = simulate_reorder(sku_df, lead_time_days=int(lead_time), safety_stock_factor=float(safety_factor))
    st.write(sim.head(50))
    # plot inventory
    fig2, ax2 = plt.subplots(figsize=(10,4))
    ax2.plot(sim["date"], sim["start_inventory"], label="Start Inventory")
    ax2.plot(sim["date"], sim["ending_inventory"], label="Ending Inventory")
    ax2.bar(sim["date"], sim["stockout_qty"], label="Stockouts", color="red", alpha=0.5)
    ax2.set_title("Simulation: Inventory & Stockouts")
    ax2.legend()
    st.pyplot(fig2)

    st.write("Simulation totals:")
    st.write({
        "total_cost": float(sim["total_cost"].sum()),
        "total_stockout": int(sim["stockout_qty"].sum()),
        "orders_placed": int((sim["order_qty"]>0).sum())
    })
