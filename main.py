from fastapi import FastAPI, HTTPException
import pandas as pd
import numpy as np
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Netflix Data API 🎬", version="1.0")

GOLD_PATH = "data/gold/"

# Load data once at startup
df_titles    = pd.read_parquet(f"{GOLD_PATH}gold_netflix_titles.parquet")
df_cast      = pd.read_parquet(f"{GOLD_PATH}gold_netflix_cast.parquet")
df_directors = pd.read_parquet(f"{GOLD_PATH}gold_netflix_directors.parquet")
df_category  = pd.read_parquet(f"{GOLD_PATH}gold_netflix_category.parquet")
df_countries = pd.read_parquet(f"{GOLD_PATH}gold_netflix_countries.parquet")

def clean_df(df):
    df = df.replace({np.nan: None})
    return df

df_titles    = clean_df(df_titles)
df_cast      = clean_df(df_cast)
df_directors = clean_df(df_directors)
df_category  = clean_df(df_category)
df_countries = clean_df(df_countries)

class Title(BaseModel):
    show_id: str
    type: Optional[str] = None
    title: Optional[str] = None
    release_year: Optional[int] = None
    rating: Optional[str] = None
    description: Optional[str] = None

@app.get("/")
def home():
    return {"message": "Welcome to Netflix Data API 🎬", "version": "1.0"}

@app.get("/titles")
def get_titles():
    return df_titles.to_dict(orient="records")

# ✅ SEARCH — must be before /{show_id}
@app.get("/titles/search")
def search_title(q: str):
    mask = (
        df_titles["title"].str.contains(q, case=False, na=False) |
        df_titles["shorttitle"].str.contains(q, case=False, na=False)
    )
    result = df_titles[mask]
    if result.empty:
        raise HTTPException(status_code=404, detail="No titles found")
    return result.to_dict(orient="records")

# ✅ FILTERS — must be before /{show_id}
@app.get("/titles/filter/type")
def filter_by_type(type: str):
    result = df_titles[df_titles["type"].str.lower() == type.lower()]
    if result.empty:
        raise HTTPException(status_code=404, detail="No titles found")
    return result.to_dict(orient="records")

@app.get("/titles/filter/rating")
def filter_by_rating(rating: str):
    result = df_titles[df_titles["rating"].str.lower() == rating.lower()]
    if result.empty:
        raise HTTPException(status_code=404, detail="No titles found")
    return result.to_dict(orient="records")

@app.get("/titles/filter/year")
def filter_by_year(year: int):
    result = df_titles[df_titles["release_year"] == year]
    if result.empty:
        raise HTTPException(status_code=404, detail="No titles found")
    return result.to_dict(orient="records")

# ⚠️ {show_id} — ALWAYS LAST!
@app.get("/titles/{show_id}")
def get_title(show_id: str):
    result = df_titles[df_titles["show_id"] == show_id]
    if result.empty:
        raise HTTPException(status_code=404, detail="Title not found")
    return result.to_dict(orient="records")[0]

@app.get("/cast")
def get_cast():
    return df_cast.to_dict(orient="records")

@app.get("/directors")
def get_directors():
    return df_directors.to_dict(orient="records")

@app.get("/directors/search")
def search_by_director(name: str):
    result = df_directors[df_directors["director"].str.contains(name, case=False, na=False)]
    if result.empty:
        raise HTTPException(status_code=404, detail="No director found")
    return result.to_dict(orient="records")

@app.get("/category")
def get_category():
    return df_category.to_dict(orient="records")

@app.get("/countries")
def get_countries():
    return df_countries.to_dict(orient="records")

@app.post("/titles")
def add_title(title: Title):
    global df_titles

    if title.show_id in df_titles["show_id"].values:
        raise HTTPException(status_code=400, detail="Title with this show_id already exists")

    new_row = {
        "duration_minutes": 0,
        "duration_seasons": 0,
        "type": title.type if title.type else "",
        "title": title.title if title.title else "",
        "date_added": "",
        "release_year": float(title.release_year) if title.release_year else 0.0,
        "rating": title.rating if title.rating else "",
        "description": title.description if title.description else "",
        "show_id": title.show_id,
        "shorttitle": title.title.split(":")[0] if title.title else "",
        "type_flag": 1 if title.type == "Movie" else 2 if title.type == "TV Show" else 0,
        "duration_ranking": 0,
        "newflag": 1,
    }

    df_titles = pd.concat([df_titles, pd.DataFrame([new_row])], ignore_index=True)
    df_titles = clean_df(df_titles)
    df_titles.to_parquet(f"{GOLD_PATH}gold_netflix_titles.parquet", index=False)

    return {"message": "Title added successfully! 🎬", "show_id": title.show_id}