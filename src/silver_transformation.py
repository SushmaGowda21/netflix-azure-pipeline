# Databricks notebook source
# MAGIC %md
# MAGIC # Silver data transformation

# COMMAND ----------

from pyspark.sql.functions import col
from pyspark.sql.types import IntegerType

# COMMAND ----------

df= spark.read.format("delta")\
      .option("header", True)\
      .option("inferSchema", True)\
      .load("abfss://bronze@sushstoragenetflix.dfs.core.windows.net/netflix_titles/")


# COMMAND ----------

df.display()

# COMMAND ----------

# MAGIC %md
# MAGIC **fill nulls**

# COMMAND ----------

df = df.fillna({"duration_minutes":0,
                 "duration_seasons":0})

# COMMAND ----------

# MAGIC %md
# MAGIC **Convert to Integer (only those columns)**

# COMMAND ----------

df= df.withColumn("duration_minutes", col("duration_minutes").cast(IntegerType()))\
    .withColumn("duration_seasons", col("duration_seasons").cast(IntegerType()))



# COMMAND ----------

# MAGIC %md
# MAGIC **Extract title after** “:” 

# COMMAND ----------

from pyspark.sql.functions import split, trim, when

# COMMAND ----------

df = df.withColumn("shorttitle", split(col("title"),":")[0])

# COMMAND ----------

# MAGIC %md
# MAGIC **rating transformation**

# COMMAND ----------

df = df.withColumn("rating", split(col("rating"),"-")[0])

# COMMAND ----------

# MAGIC %md
# MAGIC **Flag**

# COMMAND ----------

df = df.withColumn("type_flag",when(col("type") == "Movie", 1)\
    .when(col("type") == "TV Show", 2)\
    .otherwise(0)
)
display(df)

# COMMAND ----------

from pyspark.sql.functions import dense_rank, rank, col, count
from pyspark.sql.window import Window


# COMMAND ----------



w = Window.orderBy(col("duration_minutes").desc())

df = df.withColumn("duration_ranking", dense_rank().over(w))


# COMMAND ----------

df.createOrReplaceTempView("titles_temp")


# COMMAND ----------

df.createOrReplaceGlobalTempView("titles_global")


# COMMAND ----------

df = spark.sql('select * from global_temp.titles_global')

# COMMAND ----------

df =df.groupBy("type").agg(count("*").alias("total_count"))

# COMMAND ----------

df.display()

# COMMAND ----------

df.write.format("delta")\
    .mode("overwrite")\
        .option("path", "abfss://silver@sushstoragenetflix.dfs.core.windows.net/netflix_titles")\
            .save()