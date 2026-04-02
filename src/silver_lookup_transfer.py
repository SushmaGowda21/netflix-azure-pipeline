# Databricks notebook source


# COMMAND ----------

# MAGIC %md
# MAGIC #silver notebook lookup tables

# COMMAND ----------

# MAGIC %md
# MAGIC **Parametres**

# COMMAND ----------

dbutils.widgets.text("sourcefolder", "netflix_directors")
dbutils.widgets.text("targetfolder", "netflix_directors")


# COMMAND ----------

# MAGIC %md
# MAGIC **Variables**

# COMMAND ----------

src_folder = dbutils.widgets.get("sourcefolder")
tgt_folder = dbutils.widgets.get("targetfolder")

# COMMAND ----------

# MAGIC %md
# MAGIC **location= "abfss://silver@sushstoragenetflix.dfs.core.windows.net/schema"******

# COMMAND ----------

df = spark.read.format("csv")\
    .option("header", "true")\
    .option("inferSchema", "true")\
    .load(f"abfss://bronze@sushstoragenetflix.dfs.core.windows.net/{src_folder}")

# COMMAND ----------

df.write.mode("append").format("delta")\
    .option("path", f"abfss://silver@sushstoragenetflix.dfs.core.windows.net/{tgt_folder}").save()