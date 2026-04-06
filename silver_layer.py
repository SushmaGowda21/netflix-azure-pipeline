import pandas as pd
import os

BRONZE_PATH = "data/bronze/"
SILVER_PATH = "data/silver/"

os.makedirs(SILVER_PATH, exist_ok=True)

try:
    # ── 1. TITLES ──────────────────────────────────────────
    df_titles = pd.read_parquet(f"{BRONZE_PATH}netflix_titles.parquet")
    print(f"✅ Read titles — {len(df_titles)} rows")

    # Fix show_id — should be string not float (inferSchema issue)
    df_titles["show_id"] = pd.to_numeric(df_titles["show_id"], errors="coerce")\
        .astype("Int64").astype(str).str.replace("<NA>", "", regex=False)

    # Fill nulls for duration columns only (exactly like your Databricks code)
    df_titles["duration_minutes"] = pd.to_numeric(df_titles["duration_minutes"], errors="coerce").fillna(0).astype(int)
    df_titles["duration_seasons"] = pd.to_numeric(df_titles["duration_seasons"], errors="coerce").fillna(0).astype(int)

    # Short title (before ":")
    df_titles["shorttitle"] = df_titles["title"].str.split(":").str[0]

    # Rating (before "-")
    df_titles["rating"] = df_titles["rating"].str.split("-").str[0]

    # Type flag — Movie=1, TV Show=2, else=0
    df_titles["type_flag"] = df_titles["type"].map({"Movie": 1, "TV Show": 2}).fillna(0).astype(int)

    # Duration ranking — dense rank descending
    df_titles["duration_ranking"] = df_titles["duration_minutes"].rank(method="dense", ascending=False).astype(int)

    # Save
    df_titles.to_parquet(f"{SILVER_PATH}netflix_titles.parquet", index=False)
    print(f"✅ Saved netflix_titles to silver — {len(df_titles)} rows")

    # Just for display like your Databricks code (not saved)
    print("\n📊 Type counts (display only):")
    print(df_titles.groupby("type").size().reset_index(name="total_count"))

    # ── 2. LOOKUP TABLES — direct copy, no transformation ──
    lookups = ["netflix_cast", "netflix_category", "netflix_countries", "netflix_directors"]

    for file in lookups:
        df = pd.read_parquet(f"{BRONZE_PATH}{file}.parquet")
        df.to_parquet(f"{SILVER_PATH}{file}.parquet", index=False)
        print(f"✅ Saved {file} to silver — {len(df)} rows")

    print("\n🥈 Silver layer done!")

except Exception as e:
    print(f"❌ Error: {e}")