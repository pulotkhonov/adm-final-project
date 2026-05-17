# ─────────────────────────────────────────
# Spark GraphFrames Implementation
# Part 2.2.2 - PageRank and Connected Components
# ─────────────────────────────────────────

import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
from generator import generate_all
import time

# ── Tell Spark which Python to use ────────
os.environ["PYSPARK_PYTHON"] = r"C:\Users\HUAWEI\AppData\Local\Programs\Python\Python311\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Users\HUAWEI\AppData\Local\Programs\Python\Python311\python.exe"
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] = os.environ["PATH"] + r";C:\hadoop\bin"

# ── Initialize Spark Session with GraphFrames JAR ──
spark = None

def init_spark():
    global spark
    spark = SparkSession.builder \
        .appName("CityMobilityGraph") \
        .master("local[*]") \
        .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.0-s_2.12") \
        .config("spark.sql.shuffle.partitions", "50") \
        .config("spark.driver.memory", "4g") \
        .config("spark.executor.memory", "4g") \
        .getOrCreate()
    spark.sparkContext.setLogLevel("ERROR")
    print("Spark with GraphFrames initialized!")

# ── Build Graph from DataFrames ───────────
def build_graph(stations_df, trips_df):
    spark = SparkSession.getActiveSession()
    from graphframes import GraphFrame
    from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType
    
    # Convert Pandas DataFrames to Spark DataFrames
    stations_schema = StructType([
        StructField("station_id", IntegerType(), True),
        StructField("name", StringType(), True),
        StructField("city", StringType(), True),
        StructField("max_capacity", IntegerType(), True)
    ])
    
    trips_schema = StructType([
        StructField("trip_id", IntegerType(), True),
        StructField("user_id", IntegerType(), True),
        StructField("start_station_id", IntegerType(), True),
        StructField("end_station_id", IntegerType(), True),
        StructField("start_time", StringType(), True),
        StructField("end_time", StringType(), True),
        StructField("total_cost", FloatType(), True)
    ])
    
    stations_spark = spark.createDataFrame(stations_df, schema=stations_schema)
    trips_spark = spark.createDataFrame(trips_df, schema=trips_schema)
    
    # Build vertices and edges
    vertices = stations_spark.select(
        F.col("station_id").cast(StringType()).alias("id"),
        F.col("name"),
        F.col("city")
    )
    
    edges = trips_spark.select(
        F.col("start_station_id").cast(StringType()).alias("src"),
        F.col("end_station_id").cast(StringType()).alias("dst")
    )
    
    graph = GraphFrame(vertices, edges)
    print(f"Graph built with {graph.vertices.count()} vertices and {graph.edges.count()} edges!")
    return graph

# ── PageRank on Stations ──────────────────
def run_pagerank(graph):
    print("Running PageRank...")
    
    # Run PageRank with tolerance and max iterations
    pagerank = graph.pageRank(resetProbability=0.15, tol=0.01)
    
    # Get top 3 stations by PageRank score
    top3 = pagerank.vertices \
        .orderBy(F.col("pagerank").desc()) \
        .limit(3)
    
    print("Top 3 stations by PageRank:")
    top3.show()
    return top3


# ── Connected Components of Stations ──────
def run_connected_components(graph):
    spark = SparkSession.getActiveSession()
    print("Running Connected Components...")
    
    spark.sparkContext.setCheckpointDir("C:/tmp/spark_checkpoints")
    
    # Set broadcast timeout higher
    spark.conf.set("spark.sql.broadcastTimeout", "600")
    
    components = graph.connectedComponents(algorithm="graphx")
    
    # Count stations per component
    component_counts = components \
        .groupBy("component") \
        .count() \
        .orderBy(F.col("count").desc())
    
    print("Connected Components:")
    component_counts.show()
    
    total_components = component_counts.count()
    print(f"Total number of components: {total_components}")
    return components

# ── Main Block ────────────────────────────
if __name__ == "__main__":
    init_spark()
    
    print("Generating data...")
    users_df, stations_df, trips_df, events_df = generate_all()
    
    print("\nBuilding graph...")
    graph = build_graph(stations_df, trips_df)
    
    graph.vertices.cache()
    graph.edges.cache()
    graph.vertices.count()
    graph.edges.count()
    print("Graph cached!")
    
    print("\n--- PageRank ---")
    start = time.time()
    top3_pagerank = run_pagerank(graph)
    pagerank_time = time.time() - start
    print(f"PageRank time: {round(pagerank_time, 2)} seconds")
    
    print("\n--- Connected Components ---")
    start = time.time()
    components = run_connected_components(graph)
    cc_time = time.time() - start
    print(f"Connected Components time: {round(cc_time, 2)} seconds")
    
    print("\n--- Timing Summary ---")
    print(f"PageRank:             {round(pagerank_time, 2)} seconds")
    print(f"Connected Components: {round(cc_time, 2)} seconds")
    
    spark.stop()
    print("\nDone!")