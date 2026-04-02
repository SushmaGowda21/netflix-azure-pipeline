# Databricks notebook source
# MAGIC %md
# MAGIC #DTL_Notebook

# COMMAND ----------

looktabke_rule = {"rule 1": "show_id is not null"}

# COMMAND ----------

import dlt


# COMMAND ----------



@dlt.table(name="gold_netflixdirectors")
@dlt.expect_all_or_drop(looktabke_rule)
def load_directors():
    df = spark.readStream.format("delta").load("abfss://silver@sushstoragenetflix.dfs.core.windows.net/netflix_directors")
    return df

@dlt.table(name="gold_netflixcast")
@dlt.expect_all_or_drop(looktabke_rule)
def load_cast():
    df = spark.readStream.format("delta").load("abfss://silver@sushstoragenetflix.dfs.core.windows.net/netflix_cast")
    return df

@dlt.table(name="gold_netflixcategory")
@dlt.expect_all_or_drop(looktabke_rule)
def load_category():
    df = spark.readStream.format("delta").load("abfss://silver@sushstoragenetflix.dfs.core.windows.net/netflix_category")
    return df

@dlt.table(name="gold_netflixtitle")
@dlt.expect_all_or_drop(looktabke_rule)
def load_title():
    df = spark.readStream.format("delta").load("abfss://silver@sushstoragenetflix.dfs.core.windows.net/netflix_title")
    return df



# COMMAND ----------

from pyspark.sql.functions import *

# COMMAND ----------

@dlt.table
def gold_stg_netflixtitles():
    df = (
        spark.readStream
        .format("delta")
        .load("abfss://silver@sushstoragenetflix.dfs.core.windows.net/netflix_titles")
    )
    return df


# COMMAND ----------

@dlt.view
def gold_trns_netflixtitles():
    df = spark.readStream.table("LIVE.gold_stg_netflixtitles")
    
    df = df.withColumn("newflag", lit(1))
    
    return df


# COMMAND ----------

masterdata_rules = {
    "rule1": "newflag IS NOT NULL",
    "rule2": "show_id IS NOT NULL"
}

# COMMAND ----------

@dlt.table
@dlt.expect_all_or_drop(masterdata_rules)
def gold_netflixtitles():
    df = spark.readStream.table("LIVE.gold_trns_netflixtitles")
    return df