#!/usr/bin/env python3
"""
Download required Kaggle datasets and place CSVs into ./data as:
- heart.csv
- cancer.csv
- diabetes.csv

Usage:
  python scripts/download_kaggle.py              # downloads all 3
  python scripts/download_kaggle.py --heart      # only heart
  python scripts/download_kaggle.py --cancer     # only cancer
  python scripts/download_kaggle.py --diabetes   # only diabetes

Prereqs:
- pip install kaggle
- Put Kaggle credentials in ~/.kaggle/kaggle.json (or set KAGGLE_USERNAME & KAGGLE_KEY)
"""

import argparse
import os
import shutil
from pathlib import Path
from typing import Optional, List

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
TMP_DIR = Path(__file__).resolve().parents[1] / "data" / "_kaggle_tmp"
TMP_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Kaggle dataset slugs
DATASETS = {
    "heart":   "johnsmith88/heart-disease-dataset",
    "cancer":  "rabieelkharoua/cancer-prediction-dataset",
    "diabetes":"mathchi/diabetes-data-set",
}

# Preferred filename heuristics (we'll try these first if present)
PREFERRED_FILENAMES = {
    "heart":   ["heart.csv", "Heart.csv", "heart_disease.csv"],
    "cancer":  ["cancer.csv", "Cancer.csv", "cancer_data.csv", "data.csv"],
    "diabetes":["diabetes.csv", "Diabetes.csv", "diabetes.csv", "diabetes_data.csv", "diabetes.csv"],
}

def ensure_kaggle_creds():
    """
    Kaggle requires:
    - ~/.kaggle/kaggle.json  (preferred)
      OR
    - KAGGLE_USERNAME and KAGGLE_KEY env vars

    If not found, raise a helpful error.
    """
    home = Path.home()
    kaggle_json = home / ".kaggle" / "kaggle.json"
    if kaggle_json.exists():
        return
    if os.getenv("KAGGLE_USERNAME") and os.getenv("KAGGLE_KEY"):
        return
    raise SystemExit(
        "Kaggle credentials not found.\n"
        "Set them by either:\n"
        "  1) Place kaggle.json at ~/.kaggle/kaggle.json (chmod 600)\n"
        "  2) Or export KAGGLE_USERNAME and KAGGLE_KEY environment variables.\n"
        "Guide: https://www.kaggle.com/docs/api\n"
    )

def download_and_extract(slug: str, dest_dir: Path):
    """
    Use Kaggle API to download and unzip dataset into dest_dir.
    """
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    dest_dir.mkdir(parents=True, exist_ok=True)
    api.dataset_download_files(slug, path=dest_dir, unzip=True)

def pick_csv(search_dir: Path, preferred_names: List[str]) -> Optional[Path]:
    """
    Choose a CSV to use:
    1) If any preferred filename exists, use it.
    2) Else pick the first .csv found (alphabetical).
    """
    # 1) preferred
    for name in preferred_names:
        p = search_dir / name
        if p.exists() and p.suffix.lower() == ".csv":
            return p

    # 2) any csv
    csvs = sorted([p for p in search_dir.rglob("*.csv")])
    return csvs[0] if csvs else None

def fetch_one(kind: str):
    slug = DATASETS[kind]
    work_dir = TMP_DIR / kind
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    print(f"Downloading {kind} from Kaggle: {slug} ...")
    download_and_extract(slug, work_dir)

    target_name = f"{kind}.csv" if kind != "heart" else "heart.csv"
    preferred = PREFERRED_FILENAMES.get(kind, [])

    picked = pick_csv(work_dir, preferred)
    if not picked:
        raise SystemExit(
            f"Could not find any CSV in {work_dir} after downloading {slug}.\n"
            "Open the dataset page to see filenames and adjust PREFERRED_FILENAMES."
        )

    # Normalize to our desired filename mapping
    out_path = DATA_DIR / target_name
    shutil.copy2(picked, out_path)
    print(f"✔ Saved {picked.name} → {out_path}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--heart", action="store_true", help="Download only Heart dataset")
    parser.add_argument("--cancer", action="store_true", help="Download only Cancer dataset")
    parser.add_argument("--diabetes", action="store_true", help="Download only Diabetes dataset")
    args = parser.parse_args()

    ensure_kaggle_creds()

    if not any([args.heart, args.cancer, args.diabetes]):
        kinds = ["heart", "cancer", "diabetes"]
    else:
        kinds = []
        if args.heart: kinds.append("heart")
        if args.cancer: kinds.append("cancer")
        if args.diabetes: kinds.append("diabetes")

    for kind in kinds:
        fetch_one(kind)

    # Optional: clean temp
    if TMP_DIR.exists():
        shutil.rmtree(TMP_DIR)

if __name__ == "__main__":
    main()
