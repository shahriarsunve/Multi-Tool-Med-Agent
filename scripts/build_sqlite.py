import sqlite3
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DB_DIR = Path(__file__).resolve().parents[1] / "db"
DB_DIR.mkdir(exist_ok=True)

def to_sqlite(csv_path: Path, db_path: Path, table_name: str):
    df = pd.read_csv(csv_path)
    # Normalize column names
    df.columns = [c.strip().replace(" ", "_").lower() for c in df.columns]
    with sqlite3.connect(db_path) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"✔ Loaded {csv_path.name} → {db_path.name}:{table_name} ({len(df)} rows)")

def main():
    to_sqlite(DATA_DIR / "heart.csv", DB_DIR / "heart_disease.db", "heart_metrics")
    to_sqlite(DATA_DIR / "cancer.csv", DB_DIR / "cancer.db", "cancer_features")
    to_sqlite(DATA_DIR / "diabetes.csv", DB_DIR / "diabetes.db", "diabetes_metrics")

if __name__ == "__main__":
    main()