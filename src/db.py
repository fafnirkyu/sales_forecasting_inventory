from sqlalchemy import create_engine
from pathlib import Path

def sqlite_engine(path="data_out/retail_store_inventory.db"):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{Path(path).resolve()}")