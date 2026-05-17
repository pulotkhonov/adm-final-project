# ─────────────────────────────────────────
# Spark Implementation of Query 2
# Document-based (MongoDB) data source
# ─────────────────────────────────────────

import os
import time
from pymongo import MongoClient
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType
from config import MONGO_URI, MONGO_DB

# ── Tell Spark which Python to use ────────
os.environ["PYSPARK_PYTHON"] = r"C:\Users\HUAWEI\AppData\Local\Programs\Python\Python311\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Users\HUAWEI\AppData\Local\Programs\Python\Python311\python.exe"

# ── Initialize Spark Session ──────────────
spark = None
client = None
db = None

def init_spark_and_mongo():
    global spark, client, db
    spark = SparkSession.builder \
        .appName("CityMobilityQuery2") \
        .master("local[*]") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    print("Spark and MongoDB initialized!")

# ── Read Trips from MongoDB ───────────────
def read_from_mongodb():
    spark = SparkSession.getActiveSession()  
    trips_cursor = db.trips.find({}, {
        "trip_id": 1,
        "user_id": 1,
        "start_time": 1,
        "end_time": 1,
        "_id": 0
    })
    trips_list = list(trips_cursor)
    
    schema = StructType([
        StructField("trip_id", IntegerType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("start_time", StringType(), True),
        StructField("end_time", StringType(), True)
    ])
    
    trips_spark = spark.createDataFrame(trips_list, schema=schema)
    print(f"Read {trips_spark.count()} trips from MongoDB!")
    return trips_spark

# ── Read Users from MongoDB ───────────────
def read_users_from_mongodb():
    spark = SparkSession.getActiveSession()  
    users_cursor = db.users.find({}, {
        "user_id": 1,
        "name": 1,
        "surname": 1,
        "_id": 0
    })
    users_list = list(users_cursor)
    
    schema = StructType([
        StructField("user_id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("surname", StringType(), True)
    ])
    
    users_spark = spark.createDataFrame(users_list, schema=schema)
    print(f"Read {users_spark.count()} users from MongoDB!")
    return users_spark

# ── Query 2 using Spark DataFrame ─────────
def query2_dataframe(trips_spark, users_spark):
    # Calculate duration in minutes for each trip
    trips_with_duration = trips_spark.withColumn(
        "duration_minutes",
        (F.unix_timestamp(F.col("end_time"), "yyyy-MM-dd HH:mm:ss") -
         F.unix_timestamp(F.col("start_time"), "yyyy-MM-dd HH:mm:ss")) / 60
    )
    
    # Group trips by user_id
    trips_grouped = trips_with_duration.groupBy("user_id") \
        .agg(
            F.count("trip_id").alias("num_trips"),
            F.avg("duration_minutes").alias("avg_duration_minutes")
        )
    
    # Start from users — LEFT JOIN to include users with zero trips
    result = users_spark.join(trips_grouped, on="user_id", how="left")
    
    # Fill null values for users with zero trips
    result = result.fillna({"num_trips": 0, "avg_duration_minutes": 0.0})
    
    print(f"Query 2 (DataFrame): Found {result.count()} users")
    return result

# ── Main Block ────────────────────────────
if __name__ == "__main__":
    init_spark_and_mongo()
    
    print("Reading data from MongoDB...")
    trips_spark = read_from_mongodb()
    users_spark = read_users_from_mongodb()
    
    print("Caching DataFrames...")
    trips_spark.cache()
    users_spark.cache()
    trips_spark.count()
    users_spark.count()
    print("DataFrames cached!")
    
    print("\nRunning Query 2 with Spark DataFrame...")
    start = time.time()
    result_df = query2_dataframe(trips_spark, users_spark)
    result_df.collect()
    spark_time = time.time() - start
    result_df.show(3)
    print(f"Spark DataFrame time: {round(spark_time, 2)} seconds")
    
    print("\nRunning Query 2 with MongoDB native...")
    from queries_mongo import query2
    start = time.time()
    mongo_result = query2(db)
    mongo_time = time.time() - start
    print(f"MongoDB native time: {round(mongo_time, 2)} seconds")
    
    print("\n--- Timing Comparison ---")
    print(f"Spark DataFrame: {round(spark_time, 2)} seconds")
    print(f"MongoDB native:  {round(mongo_time, 2)} seconds")
    if spark_time > mongo_time:
        print(f"MongoDB is {round(spark_time/mongo_time, 1)}x faster at this scale")
    else:
        print(f"Spark is {round(mongo_time/spark_time, 1)}x faster at this scale")
    
    client.close()
    spark.stop()
    print("\nDone!")