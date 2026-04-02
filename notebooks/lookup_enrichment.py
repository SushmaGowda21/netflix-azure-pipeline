# Databricks notebook source
# MAGIC %md
# MAGIC **parameter**

# COMMAND ----------

dbutils.widgets.text("weekday", "7")

# COMMAND ----------

# MAGIC %md
# MAGIC **variable**

# COMMAND ----------

var = int(dbutils.widgets.get("weekday"))
print(var)

# COMMAND ----------

# MAGIC %md
# MAGIC **Job**

# COMMAND ----------

dbutils.jobs.taskValues.set(key="weekoutput", value=var)