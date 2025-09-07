# src/optimization.py
"""
Inventory simulation & KPI generation.

Outputs:
 - data_out/inventory_simulation.csv   (row-level merged data)
 - data_out/inventory_kpi_product.csv
 - data_out/inventory_kpi_category.csv
 - data_out/inventory_kpi_region.csv
python src/optimization.py --clean_csv data_out/retail_store_inventory_clean.csv --forecast_csv data_out/forecast_prophet.csv
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def merge_and_compute(clean_csv: str, forecast_csv: str, out_dir: str = "data_out"):
    df = pd.read_csv(clean_csv, parse_dates=["date"])
    fc = pd.read_csv(forecast_csv, parse_dates=["date"])
    merged = df.merge(fc[["date","store_id","product_id","forecast"]], on=["date","store_id","product_id"], how="left")

    # If forecast missing, fallback to rolling mean
    merged["forecast"] = merged["forecast"].fillna(merged.groupby(["store_id","product_id"])["units_sold"].transform(lambda x: x.rolling(7,min_periods=1).mean()))
    merged["ending_inventory"] = merged["inventory_level"] - merged["units_sold"]
    merged["forecast_ending_inventory"] = merged["inventory_level"] - merged["forecast"]

    # Flags
    merged["stockout"] = merged["ending_inventory"] < 0
    # define overstock as inventory > 2x typical daily sales (global mean)
    global_mean_sales = merged["units_sold"].mean()
    merged["overstock"] = merged["ending_inventory"] > (global_mean_sales * 2)

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    merged.to_csv(out_dir / "inventory_simulation.csv", index=False)
    logging.info("Saved inventory_simulation.csv")

    # KPIs
    kpi_product = merged.groupby(["store_id","product_id"]).agg({
        "stockout": "mean",
        "overstock": "mean",
        "units_sold": "sum",
        "forecast": "sum",
        "ending_inventory": "mean"
    }).reset_index()
    kpi_product.columns = ["store_id","product_id","stockout_rate","overstock_rate","total_sales","total_forecast","avg_inventory"]
    kpi_product.to_csv(out_dir / "inventory_kpi_product.csv", index=False)
    logging.info("Saved inventory_kpi_product.csv")

    # Category
    kpi_category = merged.groupby("category").agg({
        "stockout": "mean",
        "overstock": "mean",
        "units_sold": "sum",
        "forecast": "sum",
        "ending_inventory": "mean"
    }).reset_index()
    kpi_category.columns = ["category","stockout_rate","overstock_rate","total_sales","total_forecast","avg_inventory"]
    kpi_category.to_csv(out_dir / "inventory_kpi_category.csv", index=False)
    logging.info("Saved inventory_kpi_category.csv")

    # Region
    kpi_region = merged.groupby("region").agg({
        "stockout": "mean",
        "overstock": "mean",
        "units_sold": "sum",
        "forecast": "sum",
        "ending_inventory": "mean"
    }).reset_index()
    kpi_region.columns = ["region","stockout_rate","overstock_rate","total_sales","total_forecast","avg_inventory"]
    kpi_region.to_csv(out_dir / "inventory_kpi_region.csv", index=False)
    logging.info("Saved inventory_kpi_region.csv")

    return merged, kpi_product, kpi_category, kpi_region

def simulate_reorder(df_sku, lead_time_days=2, safety_stock_factor=1.2, holding_cost=0.1, stockout_cost=1.0, order_cost=10, initial_inventory=None):
    """
    Run simple reorder simulation for one SKU dataframe (df_sku must have date, units_sold, forecast, inventory_level)
    Returns simulation dataframe with day-by-day inventory, orders and costs.
    """
    df = df_sku.sort_values("date").reset_index(drop=True).copy()
    if initial_inventory is None:
        inventory = int(df.loc[0,"inventory_level"])
    else:
        inventory = int(initial_inventory)
    on_order = 0
    records = []
    for i,row in df.iterrows():
        date = row["date"]
        demand = int(row["units_sold"])
        fc = float(row.get("forecast", demand))
        start_inv = inventory
        sales = min(inventory, demand)
        stockout_qty = max(0, demand - inventory)
        inventory -= sales

        # Decide reorder
        reorder_point = int(safety_stock_factor * fc * lead_time_days)
        order_qty = 0
        if inventory < reorder_point and on_order == 0:
            order_qty = int(max(1, fc * lead_time_days * safety_stock_factor))
            on_order = order_qty

        # Receive order after lead_time_days
        if i >= lead_time_days:
            prev_order = records[i-lead_time_days]["order_qty"]
            if prev_order > 0:
                inventory += prev_order
                on_order = 0

        ending_inv = inventory
        holding = ending_inv * holding_cost
        stockout_penalty = stockout_qty * stockout_cost
        order_cost_today = order_cost if order_qty>0 else 0
        total_cost = holding + stockout_penalty + order_cost_today

        records.append({
            "date": date,
            "demand": demand,
            "forecast": fc,
            "start_inventory": start_inv,
            "sales": sales,
            "stockout_qty": stockout_qty,
            "order_qty": order_qty,
            "ending_inventory": ending_inv,
            "holding_cost": holding,
            "stockout_cost": stockout_penalty,
            "order_cost": order_cost_today,
            "total_cost": total_cost
        })

    sim_df = pd.DataFrame(records)
    return sim_df

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--clean_csv", default="data_out/retail_store_inventory_clean.csv")
    parser.add_argument("--forecast_csv", default="data_out/forecast_prophet.csv")
    args = parser.parse_args()
    merge_and_compute(args.clean_csv, args.forecast_csv)
