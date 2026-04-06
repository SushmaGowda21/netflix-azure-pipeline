# Netflix Data Pipeline — Azure Databricks, FastAPI & Docker

A medallion-architecture (Raw → Bronze → Silver → Gold) data pipeline for Netflix datasets, built on Azure Data Factory, Azure Data Lake Storage Gen2, and Databricks Unity Catalog with Delta Live Tables — and rebuilt locally with Python, FastAPI, and Docker.

---

## Repository Structure

```
.
├── src/                             # Original Azure Databricks notebooks
│   ├── bronze_autoloader.py         # Autoloader streaming ingest: Raw → Bronze
│   ├── silver_lookup_transfer.py    # Parameterised batch copy: Bronze → Silver (lookup tables)
│   ├── silver_transformation.py     # Transformations on netflix_titles: Bronze → Silver
│   └── gold_pipeline.py             # Delta Live Tables (DLT) pipeline: Silver → Gold
│
├── notebooks/                       # Databricks job utility notebooks
│   ├── lookup_logic.py              # Job utility — defines the source/target folder array
│   ├── lookup_enrichment.py         # Job utility — reads weekday widget, sets task value
│   └── if_workday_logic.py          # Conditional task — checks weekday task value
│
├── data/
│   ├── raw/                         # Raw CSV files (not pushed to Git)
│   ├── bronze/                      # Bronze Parquet files (not pushed to Git)
│   ├── silver/                      # Silver Parquet files (not pushed to Git)
│   └── gold/                        # Gold Parquet files — API reads from here
│
├── bronze_layer.py                  # Local Bronze layer — CSV → Parquet
├── silver_layer.py                  # Local Silver layer — cleaning & transformation
├── gold_layer.py                    # Local Gold layer — quality rules & final tables
├── main.py                          # FastAPI REST API — serves Gold layer data
├── dockerfile                       # Docker image definition
├── requirements.txt                 # Azure/Databricks dependencies
├── requirements-local.txt           # Local + FastAPI + Docker dependencies
├── .env.example                     # Environment variable template
├── .gitignore
└── README.md
```

---

## Architecture Overview

### Azure (Original)

```
ADLS Gen2 containers
  raw/          ← HTTP copy via ADF (source CSVs from GitHub)
  bronze/       ← Autoloader streaming output (Delta)
  silver/       ← Transformed Delta tables
  gold/         ← DLT-managed Delta tables (Unity Catalog)

Azure Data Factory
  └── ForEach pipeline (array of 5 Netflix folders)
        ├── Validation activity  — confirms file exists in raw/
        ├── Copy activity        — HTTP source → ADLS sink
        ├── Web activity         — trigger or notify
        └── Set Variable         — tracks pipeline state

Databricks (Unity Catalog + DLT)
  └── netflix_catalog.net_schema
        ├── Bronze Autoloader notebook
        ├── Silver transformation notebook
        └── Gold DLT pipeline (expect_all_or_drop quality rules)
```

### Local (Rebuilt — No Azure Cost)

```
Raw CSV files (data/raw/)
      ↓
🥉 Bronze Layer  →  bronze_layer.py  →  data/bronze/ (Parquet)
      ↓
🥈 Silver Layer  →  silver_layer.py  →  data/silver/ (Parquet, cleaned)
      ↓
🥇 Gold Layer    →  gold_layer.py    →  data/gold/   (Parquet, quality rules)
      ↓
⚡ FastAPI        →  main.py          →  localhost:8000
      ↓
🐳 Docker         →  dockerfile       →  runs anywhere!
```

---

## Local Setup — Run Without Azure

### Prerequisites
- Python 3.11+
- Docker Desktop

### Step 1 — Clone and Setup

```bash
git clone https://github.com/SushmaGowda21/netflix-azure-pipeline.git
cd netflix-azure-pipeline
python -m venv venv
venv\Scripts\activate
pip install -r requirements-local.txt
```

### Step 2 — Add Raw Data

Download the Netflix CSV files and place them in `data/raw/`:
- `netflix_titles.csv`
- `netflix_cast.csv`
- `netflix_category.csv`
- `netflix_countries.csv`
- `netflix_directors.csv`

### Step 3 — Run the Pipeline

```bash
python bronze_layer.py
python silver_layer.py
python gold_layer.py
```

### Step 4 — Run FastAPI

```bash
uvicorn main:app --reload
```

API at: `http://localhost:8000`
Swagger UI at: `http://localhost:8000/docs`

---

## REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Welcome message |
| GET | `/titles` | All Netflix titles |
| GET | `/titles/search?q=batman` | Search titles by name |
| GET | `/titles/filter/type?type=Movie` | Filter by type |
| GET | `/titles/filter/rating?rating=R` | Filter by rating |
| GET | `/titles/filter/year?year=2020` | Filter by release year |
| GET | `/titles/{show_id}` | Get one title by ID |
| GET | `/cast` | All cast members |
| GET | `/directors` | All directors |
| GET | `/directors/search?name=Nolan` | Search directors by name |
| GET | `/category` | All categories |
| GET | `/countries` | All countries |
| POST | `/titles` | Add a new title |

### POST /titles — Example

```json
{
    "show_id": "s9998",
    "type": "Movie",
    "title": "Saptha Sagaradache Yello",
    "release_year": 2023,
    "rating": "U/A",
    "description": "A Kannada romantic drama directed by Rakshith Shetty"
}
```

---

## Docker

### Build Image

```bash
docker build -t netflix-api .
```

### Run Container

```bash
docker run -p 8000:8000 netflix-api
```

API at: `http://localhost:8000`

---

## Silver Layer — Transformations

| Transformation | Column | Details |
|---|---|---|
| Fill nulls | duration_minutes, duration_seasons | Replaced with 0 |
| Type cast | duration_minutes, duration_seasons | Converted to Integer |
| Short title | shorttitle | Extracted text before `:` in title |
| Rating clean | rating | Extracted text before `-` in rating |
| Type flag | type_flag | Movie=1, TV Show=2, else=0 |
| Duration rank | duration_ranking | Dense rank by duration descending |

---

## Gold Layer — Quality Rules

| Rule | Column | Action |
|---|---|---|
| show_id IS NOT NULL | show_id | Drop rows where null |
| newflag IS NOT NULL | newflag | Drop rows where null |
| newflag = 1 | newflag | Added as constant column |

---

## Gold Tables

| Table | Rows | Description |
|---|---|---|
| gold_netflix_titles | 6,236 | Main Netflix titles |
| gold_netflix_cast | 44,311 | Cast members per title |
| gold_netflix_category | 13,670 | Categories per title |
| gold_netflix_countries | 7,179 | Countries per title |
| gold_netflix_directors | 4,852 | Directors per title |

---

## Azure Setup

### Prerequisites

See `requirements.txt` for Python dependencies. You also need:

- Azure subscription with Contributor access
- Azure CLI or portal access
- Databricks workspace (Premium tier for Unity Catalog)
- A GitHub personal access token (if using private repos)

### 1. Azure Resources

1. Create a **Resource Group**.
2. Create a **Storage Account** — enable *Hierarchical Namespace* (ADLS Gen2).
3. Create four containers: `raw`, `bronze`, `silver`, `gold`.
4. Create an **Azure Data Factory** instance and launch the ADF Studio.

### 2. ADF Linked Services

| Name | Type | Auth |
|---|---|---|
| `github` | HTTP | Anonymous (base URL = raw GitHub content URL) |
| `adls_netflix` | Azure Data Lake Storage Gen2 | Managed Identity |

### 3. ADF Pipeline

- **Parameters**: array of objects (`sourcefolder`, `targetfolder`) — defined in `lookup_logic.py`.
- **Activities in order**:
  1. **Validation** — confirms source file exists in `raw/` container.
  2. **ForEach** (sequential, array from parameter) containing a **Copy** activity:
     - Source: HTTP linked service, CSV format, relative URL built dynamically from array item.
     - Sink: ADLS linked service, CSV format, file path built from `targetfolder` parameter.
  3. **Web Activity** — optional HTTP callback or Azure Function trigger.
  4. **Set Variable** — records pipeline run status.
- Set **Timeout**, **Retry** (3 retries, 30-second intervals) on the Copy activity.

### 4. Databricks Unity Catalog

1. In the **Databricks Account Console**, navigate to **Metastore** → create or assign a Unity Catalog metastore.
2. Set the **ADLS Gen2 path** and the **Access Connector ID**.
3. In **Entra ID**, find the Access Connector's managed identity and assign it the **Storage Blob Data Contributor** role on the storage account.
4. In Unity Catalog:
   - Create **External Credential** pointing to the managed identity.
   - Create **External Locations** for `bronze/`, `silver/`, `gold/` containers.
5. Assign the workspace to the metastore; grant catalog access to all account users as needed.

### 5. Databricks Catalog & Schema

```sql
CREATE CATALOG IF NOT EXISTS netflix_catalog;
CREATE SCHEMA IF NOT EXISTS netflix_catalog.net_schema;
```

### 6. Running the Notebooks

| Notebook | Trigger | Notes |
|---|---|---|
| `bronze_autoloader.py` | Streaming / scheduled | Reads from `raw/`, writes to `bronze/` as Delta |
| `silver_lookup_transfer.py` | ADF ForEach job (parameterised) | Pass `sourcefolder` & `targetfolder` widgets |
| `silver_transformation.py` | Scheduled job | Transforms `netflix_titles`; writes to `silver/` |
| `gold_pipeline.py` | DLT pipeline | Attach to a DLT pipeline in Databricks; runs continuously or triggered |
| `lookup_logic.py` | Job task (returns array) | Run before ForEach tasks; sets `my_arr` task value |
| `lookup_enrichment.py` | Job task | Sets `weekoutput` task value from widget |
| `if_workday_logic.py` | Conditional job task | Reads `weekoutput`; gates downstream tasks |

---

## Changelog

### Bug Fixes Applied (Azure Version)

| # | File | Fix |
|---|---|---|
| 1 | `gold_pipeline.py` | Removed duplicate `@dlt.table` definition for `gold_stg_netflixtitles` |
| 2 | `gold_pipeline.py` | Renamed all `myfunc()` loader functions to descriptive names: `load_directors`, `load_cast`, `load_category`, `load_title` |
| 3 | `silver_transformation.py` | Fixed SQL query from `global_temp.global_view` → `global_temp.titles_global` to match the registered view name |
