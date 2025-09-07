"""
Per-store/per-product forecasting using Prophet.
Outputs:
 - data_out/forecast_prophet.csv  (date, store_id, product_id, forecast)
# quick test: only first 20 store/product combos
python src/forecasting.py data_out/retail_store_inventory_clean.csv --out_csv data_out/forecast_prophet.csv --min_points 30 --limit_groups 20

# full run (may take long for many SKUs)
python src/forecasting.py data_out/retail_store_inventory_clean.csv --out_csv data_out/forecast_prophet.csv --min_points 30
"""

import argparse
from pathlib import Path
import pandas as pd
from prophet import Prophet
from sklearn.metrics import mean_squared_error, mean_absolute_percentage_error
from tqdm import tqdm
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

def run(clean_csv: str, out_csv: str = "data_out/forecast_prophet.csv", min_points: int = 30, limit_groups: int = None):
    clean_csv = Path(clean_csv)
    out_csv = Path(out_csv)
    df = pd.read_csv(clean_csv, parse_dates=["date"])
    df = df.sort_values(["store_id","product_id","date"])

    groups = list(df.groupby(["store_id","product_id"]))
    if limit_groups:
        groups = groups[:limit_groups]

    forecasts = []
    logging.info("Starting forecasting for %d groups (min_points=%d)", len(groups), min_points)
    for (store, product), g in tqdm(groups):
        g = g.sort_values("date")
        if len(g) < min_points:
            # skip small series
            continue
        prophet_df = g[["date","units_sold"]].rename(columns={"date":"ds","units_sold":"y"})
        try:
            model = Prophet(daily_seasonality=True, yearly_seasonality=True)
            model.fit(prophet_df)
            pred = model.predict(prophet_df[["ds"]])
            yhat = pred["yhat"].values
            tmp = g[["date","store_id","product_id","category","region"]].copy()
            tmp["forecast"] = yhat
            forecasts.append(tmp)
        except Exception as e:
            logging.warning("Failed for store=%s product=%s: %s", store, product, e)
            continue

    if len(forecasts) == 0:
        raise RuntimeError("No forecasts generated. Check data or lower min_points/limit_groups.")

    fc_df = pd.concat(forecasts, ignore_index=True)
    # standardize column names
    fc_df = fc_df.rename(columns={"date":"date","store_id":"store_id","product_id":"product_id","forecast":"forecast"})
    fc_df.to_csv(out_csv, index=False)
    logging.info("Saved forecasts to %s", out_csv)

    # Optional: evaluate on rows where forecast exists and units_sold present
    merged = df.merge(fc_df[["date","store_id","product_id","forecast"]], on=["date","store_id","product_id"], how="left")
    merged_eval = merged.dropna(subset=["forecast"])
    if len(merged_eval)>0:
        rmse = mean_squared_error(merged_eval["units_sold"], merged_eval["forecast"])
        mape = mean_absolute_percentage_error(merged_eval["units_sold"], merged_eval["forecast"])
        logging.info("Global eval on fitted data: RMSE=%.3f MAPE=%.2f%%", rmse, mape*100)
    else:
        logging.info("No merged rows for evaluation.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("clean_csv", help="Cleaned CSV produced by data_cleaning")
    parser.add_argument("--out_csv", default="data_out/forecast_prophet.csv")
    parser.add_argument("--min_points", type=int, default=30)
    parser.add_argument("--limit_groups", type=int, default=None, help="Limit number of store/product groups (for testing)")
    args = parser.parse_args()
    run(args.clean_csv, args.out_csv, args.min_points, args.limit_groups)
