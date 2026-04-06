import pandas as pd
import os

RAW_PATH = "data/raw/"
BRONZE_PATH = "data/bronze/"

os.makedirs(BRONZE_PATH, exist_ok=True)

files = [
    "netflix_titles",
    "netflix_cast",
    "netflix_category",
    "netflix_countries",
    "netflix_directors"
]

for file in files:
    print(f"Loading {file}...")
    df = pd.read_csv(f"{RAW_PATH}{file}.csv")
    df.to_parquet(f"{BRONZE_PATH}{file}.parquet", index=False)
    print(f"✅ Saved {file} to bronze — {len(df)} rows")

print("\n🥉 Bronze layer done!")