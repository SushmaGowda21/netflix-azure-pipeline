import pandas as pd
import os

SILVER_PATH = "data/silver/"
GOLD_PATH = "data/gold/"

os.makedirs(GOLD_PATH, exist_ok=True)

try:
    # ── 1. TITLES ──────────────────────────────────────────
    df_titles = pd.read_parquet(f"{SILVER_PATH}netflix_titles.parquet")

    # Add new flag (like your DLT pipeline)
    df_titles["newflag"] = 1

    # Drop rows where show_id is null (your DLT rule)
    df_titles = df_titles.dropna(subset=["show_id"])

    df_titles.to_parquet(f"{GOLD_PATH}gold_netflix_titles.parquet", index=False)
    print(f"✅ Saved gold_netflix_titles — {len(df_titles)} rows")

    # ── 2. LOOKUP TABLES ───────────────────────────────────
    lookups = ["netflix_cast", "netflix_category", "netflix_countries", "netflix_directors"]

    for file in lookups:
        df = pd.read_parquet(f"{SILVER_PATH}{file}.parquet")
        df = df.dropna(subset=["show_id"])
        df.to_parquet(f"{GOLD_PATH}gold_{file}.parquet", index=False)
        print(f"✅ Saved gold_{file} — {len(df)} rows")

    print("\n🥇 Gold layer done!")

except Exception as e:
    print(f"❌ Error: {e}")