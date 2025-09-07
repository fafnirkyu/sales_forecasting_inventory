"""
Data cleaning & canonicalization for retail_store_inventory.csv
Outputs:
 - data_out/retail_store_inventory_clean.csv (canonical column names)
 - data_out/retail_store_inventory.db (sqlite with table retail_cleaned)
python src/data_cleaning.py data/retail_store_inventory.csv --out_dir data_out --sqlite data_out/retail_store_inventory.db
"""
import argparse
from pathlib import Path
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

# Candidate column name mapping for detection
CANDIDATES = {
    "date": ["date", "day", "timestamp"],
    "store_id": ["store_id", "store id", "store", "storeid"],
    "product_id": ["product_id", "product id", "product", "sku"],
    "units_sold": ["units_sold", "units sold", "units", "sales", "quantity"],
    "inventory_level": ["inventory_level", "inventory level", "inventory", "stock", "stock_level"],
    "price": ["price", "unit_price", "unit price", "sale_price"],
    "promotion": ["promo", "promotion", "is_promo", "on_promo", "holiday/promotion", "holiday_promotion"],
    "holiday": ["holiday", "is_holiday", "holiday_flag"],
    "category": ["category", "product_category"],
    "region": ["region", "store_region"]
}

CANONICAL = {
    "date": "date",
    "store_id": "store_id",
    "product_id": "product_id",
    "units_sold": "units_sold",
    "inventory_level": "inventory_level",
    "price": "price",
    "promotion": "is_promo",
    "holiday": "is_holiday",
    "category": "category",
    "region": "region"
}

def normalize_cols(df):
    new_cols = {c: c.strip() for c in df.columns}
    df = df.rename(columns=new_cols)
    return df

def guess_column(columns, candidate_list):
    cols = [c.lower().strip() for c in columns]
    for cand in candidate_list:
        if cand.lower() in cols:
            # return original column name (case-sensitive)
            return columns[cols.index(cand.lower())]
    # fallback: find a column that contains substring
    for cand in candidate_list:
        for i,c in enumerate(cols):
            if cand.lower().replace(" ", "") in c.replace(" ", ""):
                return columns[i]
    return None

def map_columns(df):
    orig_cols = list(df.columns)
    found = {}
    for key, candidates in CANDIDATES.items():
        col = guess_column(orig_cols, candidates)
        found[key] = col
    return found

def to_numeric_safe(series):
    return pd.to_numeric(series, errors="coerce")

def run(input_csv: str, out_dir: str = "data_out", sqlite_path: str = "data_out/retail_store_inventory.db"):
    input_csv = Path(input_csv)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_csv)
    logging.info(f"Loaded raw CSV: {input_csv} -> shape {df.shape}")

    df = normalize_cols(df)

    guessed = map_columns(df)
    logging.info("Guessed columns: %s", guessed)

    # date parse
    date_col = guessed.get("date")
    if date_col is None:
        raise ValueError("Could not find a date-like column. Please ensure dataset has a date column.")
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    logging.info("Date parsed: min=%s max=%s", df[date_col].min(), df[date_col].max())

    # ensure core ids exist
    store_col = guessed.get("store_id")
    prod_col = guessed.get("product_id")
    if store_col is None or prod_col is None:
        raise ValueError("Could not detect store_id and/or product_id columns.")

    # numeric columns
    units_col = guessed.get("units_sold")
    if units_col:
        df[units_col] = to_numeric_safe(df[units_col]).fillna(0).astype(int)
    else:
        df["units_sold"] = 0
        units_col = "units_sold"

    inv_col = guessed.get("inventory_level")
    if inv_col:
        df[inv_col] = to_numeric_safe(df[inv_col]).fillna(0).astype(int)
    else:
        df["inventory_level"] = 0
        inv_col = "inventory_level"

    price_col = guessed.get("price")
    if price_col:
        df[price_col] = to_numeric_safe(df[price_col]).fillna(0.0)
    else:
        df["price"] = np.nan
        price_col = "price"

    # promotion & holiday
    promo_col = guessed.get("promotion")
    if promo_col:
        df[promo_col] = df[promo_col].fillna(0).astype(int)
    else:
        df["is_promo"] = 0
        promo_col = "is_promo"

    hol_col = guessed.get("holiday")
    if hol_col:
        df[hol_col] = df[hol_col].fillna(0).astype(int)
    else:
        df["is_holiday"] = 0
        hol_col = "is_holiday"

    # category & region optional
    cat_col = guessed.get("category")
    if cat_col is None:
        df["category"] = "UNKNOWN"
        cat_col = "category"
    region_col = guessed.get("region")
    if region_col is None:
        df["region"] = "UNKNOWN"
        region_col = "region"

    # derived revenue
    if price_col:
        df["revenue"] = df[units_col] * df[price_col]
    else:
        df["revenue"] = np.nan

    # stockout flag (inventory at start of day)
    df["stockout_flag"] = df[units_col] > df[inv_col]

    # rename to canonical names
    rename_map = {
        date_col: "date",
        store_col: "store_id",
        prod_col: "product_id",
        units_col: "units_sold",
        inv_col: "inventory_level",
        price_col: "price",
        promo_col: "is_promo",
        hol_col: "is_holiday",
        cat_col: "category",
        region_col: "region"
    }
    df = df.rename(columns=rename_map)

    # keep only canonical columns (and extras)
    keep = ["date","store_id","product_id","category","region","units_sold","inventory_level","price","is_promo","is_holiday","revenue","stockout_flag"]
    for c in keep:
        if c not in df.columns:
            df[c] = np.nan

    df = df[keep]
    df = df.sort_values(["store_id","product_id","date"]).reset_index(drop=True)

    # save cleaned csv
    cleaned_csv = Path(out_dir) / "retail_store_inventory_clean.csv"
    df.to_csv(cleaned_csv, index=False)
    logging.info("Saved cleaned CSV to %s", cleaned_csv)

    # write to sqlite for Power BI
    engine = create_engine(f"sqlite:///{Path(sqlite_path).resolve()}")
    df.to_sql("retail_cleaned", engine, if_exists="replace", index=False)
    logging.info("Saved table retail_cleaned to sqlite db: %s", sqlite_path)

    # create basic indexes
    with engine.connect() as conn:
        try:
            conn.execute("CREATE INDEX IF NOT EXISTS idx_store_date ON retail_cleaned (store_id, date);")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_prod_date ON retail_cleaned (product_id, date);")
        except Exception as e:
            logging.warning("Index creation failed: %s", e)

    print("Cleaning finished. cleaned CSV:", cleaned_csv, "sqlite:", sqlite_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input_csv", help="Path to raw CSV (data/retail_store_inventory.csv)")
    parser.add_argument("--out_dir", default="data_out", help="Output directory")
    parser.add_argument("--sqlite", default="data_out/retail_store_inventory.db", help="Sqlite path")
    args = parser.parse_args()
    run(args.input_csv, args.out_dir, args.sqlite)
