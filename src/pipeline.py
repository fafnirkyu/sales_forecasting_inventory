import pandas as pd
from pathlib import Path
from prophet import Prophet

def run_pipeline(data_path: str = "data/retail_store_inventory.csv",
                 output_path: str = "data/forecast.csv") -> None:
    """Run full forecasting pipeline and save results."""
    print("📊 Loading data...")
    df = pd.read_csv(data_path, parse_dates=["Date"])
    df = df.groupby("Date", as_index=False)["Units Sold"].sum()

    print("🤖 Training Prophet model...")
    prophet_df = df.rename(columns={"Date": "ds", "Units Sold": "y"})
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(prophet_df)

    print("🔮 Forecasting future...")
    future = model.make_future_dataframe(periods=30)
    forecast = model.predict(future)

    forecast[["ds", "yhat"]].rename(columns={"ds": "Date", "yhat": "Forecast"}).to_csv(output_path, index=False)
    print(f"✅ Forecast saved to {output_path}")
