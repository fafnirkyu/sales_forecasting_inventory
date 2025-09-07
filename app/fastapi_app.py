# to run: uvicorn app.fastapi_app:app --reload --port 8000
from fastapi import FastAPI, Query
import pandas as pd
from pydantic import BaseModel
from src.optimization import simulate_reorder
from functools import lru_cache

app = FastAPI(title="Retail Forecast API")

@lru_cache(maxsize=1)
def load_merged():
    clean = pd.read_csv("data_out/retail_store_inventory_clean.csv", parse_dates=["date"])
    forecast = pd.read_csv("data_out/forecast_prophet.csv", parse_dates=["date"])
    merged = clean.merge(forecast, on=["date","store_id","product_id"], how="left")
    merged["forecast"] = merged["forecast"].fillna(merged.groupby(["store_id","product_id"])["units_sold"].transform(lambda x: x.rolling(7,min_periods=1).mean()))
    return merged

@app.get("/forecast")
def get_forecast(store_id: str, product_id: str, start: str = None, end: str = None):
    merged = load_merged()
    df = merged[(merged["store_id"]==store_id) & (merged["product_id"]==product_id)]
    if start:
        df = df[df["date"]>=pd.to_datetime(start)]
    if end:
        df = df[df["date"]<=pd.to_datetime(end)]
    return df[["date","units_sold","forecast"]].to_dict(orient="records")

class SimRequest(BaseModel):
    store_id: str
    product_id: str
    lead_time_days: int = 2
    safety_stock_factor: float = 1.2

@app.post("/simulate")
def simulate(sim: SimRequest):
    merged = load_merged()
    df = merged[(merged["store_id"]==sim.store_id) & (merged["product_id"]==sim.product_id)].sort_values("date")
    sim_df = simulate_reorder(df, lead_time_days=sim.lead_time_days, safety_stock_factor=sim.safety_stock_factor)
    # return small summary
    return {
        "total_cost": float(sim_df["total_cost"].sum()),
        "total_stockout": int(sim_df["stockout_qty"].sum()),
        "orders_placed": int((sim_df["order_qty"]>0).sum())
    }


