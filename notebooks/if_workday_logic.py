# Databricks notebook source
var = dbutils.jobs.taskValues.get(taskKey = "weekdaylookup", key = "weekoutput", debugValue=True)
print(var)
