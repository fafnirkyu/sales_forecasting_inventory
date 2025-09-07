import sqlite3
import pandas as pd

def init_db():
    conn = sqlite3.connect("data_out/retail.db")

    # Load clean + forecast data
    clean = pd.read_csv("data_out/retail_store_inventory_clean.csv", parse_dates=["date"])
    forecast = pd.read_csv("data_out/forecast_prophet.csv", parse_dates=["date"])

    # Write to SQL tables
    clean.to_sql("inventory_clean", conn, if_exists="replace", index=False)
    forecast.to_sql("forecast", conn, if_exists="replace", index=False)

    conn.commit()
    conn.close()
    print("✅ Database initialized at data_out/retail.db")

if __name__ == "__main__":
    init_db()
