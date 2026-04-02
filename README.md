# Netflix Data Pipeline — Azure Databricks & ADF

A medallion-architecture (Raw → Bronze → Silver → Gold) data pipeline for Netflix datasets, built on Azure Data Factory, Azure Data Lake Storage Gen2, and Databricks Unity Catalog with Delta Live Tables.

---

## Repository Structure

```
.
├── bronze_autoloader.py        # Autoloader streaming ingest: Raw → Bronze
├── silver_lookup_transfer.py   # Parameterised batch copy: Bronze → Silver (lookup tables)
├── silver_transformation.py    # Transformations on netflix_titles: Bronze → Silver
├── gold_pipeline.py            # Delta Live Tables (DLT) pipeline: Silver → Gold
├── lookup_logic.py             # Job utility — defines the source/target folder array
├── lookup_enrichment.py        # Job utility — reads weekday widget, sets task value
├── if_workday_logic.py         # Conditional task — checks weekday task value
├── README.md
└── requirements.txt
```

---

## Architecture Overview

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

---

## Prerequisites

See `requirements.txt` for Python dependencies. You also need:

- Azure subscription with Contributor access
- Azure CLI or portal access
- Databricks workspace (Premium tier for Unity Catalog)
- A GitHub personal access token (if using private repos)

---

## Setup Steps

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

### Bug Fixes Applied

| # | File | Fix |
|---|---|---|
| 1 | `gold_pipeline.py` | Removed duplicate `@dlt.table` definition for `gold_stg_netflixtitles` |
| 2 | `gold_pipeline.py` | Renamed all `myfunc()` loader functions to descriptive names: `load_directors`, `load_cast`, `load_category`, `load_title` |
| 3 | `silver_transformation.py` | Fixed SQL query from `global_temp.global_view` → `global_temp.titles_global` to match the registered view name |

---

