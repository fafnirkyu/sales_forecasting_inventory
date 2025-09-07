# main.py
"""
Run the full pipeline:
1) clean raw CSV -> data_out/retail_store_inventory_clean.csv
2) forecast per SKU -> data_out/forecast_prophet.csv
3) compute inventory KPIs -> data_out/inventory_*.csv
"""

import subprocess
import sys
from pathlib import Path

def run_cmd(cmd):
    print("RUN:", cmd)
    r = subprocess.run(cmd, shell=True)
    if r.returncode != 0:
        raise SystemExit(f"Command failed: {cmd}")

if __name__ == "__main__":
    Path("data_out").mkdir(exist_ok=True)
    # 1) cleaning
    run_cmd(f"{sys.executable} src/data_cleaning.py data/retail_store_inventory.csv --out_dir data_out --sqlite data_out/retail_store_inventory.db")
    # 2) forecasting (limit groups for first run can be removed)
    run_cmd(f"{sys.executable} src/forecasting.py data_out/retail_store_inventory_clean.csv --out_csv data_out/forecast_prophet.csv --min_points 30")
    # 3) optimization/kpis
    run_cmd(f"{sys.executable} -c \"from src.optimization import merge_and_compute; merge_and_compute('data_out/retail_store_inventory_clean.csv','data_out/forecast_prophet.csv')\"")
    print('Pipeline finished. Check data_out/')
