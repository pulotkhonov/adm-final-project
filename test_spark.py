from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("test") \
    .getOrCreate()

print("Spark works!")
spark.stop()