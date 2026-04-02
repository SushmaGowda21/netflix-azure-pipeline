# Databricks notebook source
# MAGIC %md
# MAGIC # incremental data loading using Autoloader

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE SCHEMA if not EXISTS netflix_catalog.net_schema;

# COMMAND ----------

schema_location     = "abfss://silver@sushstoragenetflix.dfs.core.windows.net/schema"
checkpoint_location = "abfss://silver@sushstoragenetflix.dfs.core.windows.net/checkpoints"


# COMMAND ----------



df  =spark.readStream\
    .format("cloudFiles")\
    .option("cloudFiles.format", "csv")\
    .option("cloudFiles.schemaLocation", checkpoint_location)\
    .load("abfss://raw@sushstoragenetflix.dfs.core.windows.net")

# COMMAND ----------

display(df, checkpointLocation=checkpoint_location)

# COMMAND ----------


df.writeStream\
 .option("checkpointLocation", checkpoint_location)\
   .trigger(processingTime="10 seconds")\
   .start("abfss://bronze@sushstoragenetflix.dfs.core.windows.net/netflix_titles")

# COMMAND ----------

