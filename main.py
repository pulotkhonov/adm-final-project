# ─────────────────────────────────────────
# Main Automation Script
# City Mobility Platform - All 36 Combinations
# ─────────────────────────────────────────

import os
import time
import csv
import psutil

# ── Spark Environment Setup ───────────────
os.environ["PYSPARK_PYTHON"] = r"C:\Users\HUAWEI\AppData\Local\Programs\Python\Python311\python.exe"
os.environ["PYSPARK_DRIVER_PYTHON"] = r"C:\Users\HUAWEI\AppData\Local\Programs\Python\Python311\python.exe"
os.environ["HADOOP_HOME"] = r"C:\hadoop"
os.environ["PATH"] = os.environ["PATH"] + r";C:\hadoop\bin"

# ── Spark Session — initialize FIRST before any imports ──
from pyspark.sql import SparkSession
spark = SparkSession.builder \
    .appName("CityMobility") \
    .master("local[*]") \
    .config("spark.jars.packages", "graphframes:graphframes:0.8.2-spark3.0-s_2.12") \
    .config("spark.sql.shuffle.partitions", "50") \
    .config("spark.driver.memory", "4g") \
    .config("spark.executor.memory", "4g") \
    .getOrCreate()
spark.sparkContext.setLogLevel("ERROR")
print("Spark session initialized!")

# ── Import all modules ────────────────────
from generator import generate_all
from load_postgres import get_connection as pg_connect, create_tables
from load_postgres import load_users as pg_load_users, load_stations as pg_load_stations
from load_postgres import load_trips as pg_load_trips, load_events as pg_load_events
from load_mongo import get_connection as mongo_connect
from load_mongo import load_users as mongo_load_users, load_trips as mongo_load_trips
from load_neo4j import get_connection as neo4j_connect, clear_db, create_indexes
from load_neo4j import load_users as neo4j_load_users, load_stations as neo4j_load_stations
from load_neo4j import load_trips as neo4j_load_trips
from load_neo4j import load_performed, load_starts_at, load_ends_at
from queries_postgres import query1 as pg_q1, query2 as pg_q2, query3 as pg_q3, query4 as pg_q4
from queries_mongo import query1_lookup, query2 as mongo_q2, query3 as mongo_q3, query4 as mongo_q4
from queries_neo4j import query1 as neo4j_q1, query2 as neo4j_q2
from spark_doc import read_from_mongodb, read_users_from_mongodb, query2_dataframe
from spark_graph import build_graph, run_pagerank, run_connected_components

# ── Memory Helper ─────────────────────────
def get_memory_mb():
    process = psutil.Process(os.getpid())
    return round(process.memory_info().rss / 1024 / 1024, 2)

# ── Results Storage ───────────────────────
results = []

def save_result(n_users, n_trips, events_per_trip, db, query, time_seconds):
    results.append({
        "n_users": n_users,
        "n_trips": n_trips,
        "events_per_trip": events_per_trip,
        "db": db,
        "query": query,
        "time_seconds": round(time_seconds, 4),
        "memory_mb": get_memory_mb()
    })

def save_results_to_csv():
    file_exists = os.path.exists("results.csv")
    with open("results.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "n_users", "n_trips", "events_per_trip",
            "db", "query", "time_seconds", "memory_mb"
        ])
        if not file_exists:
            writer.writeheader()
        writer.writerows(results[-16:])  
    print(f"Results appended to results.csv ({len(results)} total records)")

# ── Scale Combinations ────────────────────

# ── TEST combination ──
combinations = [(10000, 10000, 2)]

# ── Loop through 36 combinations────────────

# combinations = []
# for n_users in [1000, 10000, 50000]:
#     for n_trips in [10000, 50000, 100000]:
#         for events_per_trip in [0, 2, 5, 10]:
#             combinations.append((n_users, n_trips, events_per_trip))
# print(f"Remaining combinations: {len(combinations)}")

# ── Main Loop ─────────────────────────────
if __name__ == "__main__":
    total_start = time.time()
    # Initialize persistent connections
    neo4j_driver = neo4j_connect()

    for idx, (n_users, n_trips, events_per_trip) in enumerate(combinations):
        print(f"\n{'='*60}")
        print(f"Combination {idx+1}/{len(combinations)}: "
              f"{n_users} users, {n_trips} trips, {events_per_trip} events/trip")
        print(f"{'='*60}")

        # ── Generate Data ─────────────────
        print("Generating data...")
        users_df, stations_df, trips_df, events_df = generate_all(
            n_users=n_users,
            n_trips=n_trips,
            events_per_trip=events_per_trip
        )

        # ── PostgreSQL ────────────────────
        print("\n--- PostgreSQL ---")
        pg_conn = pg_connect()
        pg_cursor = create_tables(pg_conn)

        start = time.time()
        pg_load_users(pg_conn, pg_cursor, users_df)
        pg_load_stations(pg_conn, pg_cursor, stations_df)
        pg_load_trips(pg_conn, pg_cursor, trips_df)
        pg_load_events(pg_conn, pg_cursor, events_df)
        save_result(n_users, n_trips, events_per_trip, "postgres", "load", time.time() - start)

        start = time.time()
        pg_q1(pg_cursor)
        save_result(n_users, n_trips, events_per_trip, "postgres", "query1", time.time() - start)

        start = time.time()
        pg_q2(pg_cursor)
        save_result(n_users, n_trips, events_per_trip, "postgres", "query2", time.time() - start)

        start = time.time()
        pg_q3(pg_cursor)
        save_result(n_users, n_trips, events_per_trip, "postgres", "query3", time.time() - start)

        start = time.time()
        pg_q4(pg_cursor)
        save_result(n_users, n_trips, events_per_trip, "postgres", "query4", time.time() - start)

        pg_cursor.close()
        pg_conn.close()
        print("PostgreSQL done!")

        # ── MongoDB ───────────────────────
        print("\n--- MongoDB ---")
        mongo_client, mongo_db = mongo_connect()

        start = time.time()
        mongo_load_users(mongo_db, users_df)
        mongo_load_trips(mongo_db, trips_df, stations_df, events_df)
        save_result(n_users, n_trips, events_per_trip, "mongodb", "load", time.time() - start)

        start = time.time()
        query1_lookup(mongo_db)
        save_result(n_users, n_trips, events_per_trip, "mongodb", "query1_lookup", time.time() - start)

        start = time.time()
        mongo_q2(mongo_db)
        save_result(n_users, n_trips, events_per_trip, "mongodb", "query2", time.time() - start)

        start = time.time()
        mongo_q3(mongo_db)
        save_result(n_users, n_trips, events_per_trip, "mongodb", "query3", time.time() - start)

        start = time.time()
        mongo_q4(mongo_db)
        save_result(n_users, n_trips, events_per_trip, "mongodb", "query4", time.time() - start)

        mongo_client.close()
        print("MongoDB done!")

        # ── Neo4j ─────────────────────────
        print("\n--- Neo4j ---")
        clear_db(neo4j_driver)
        create_indexes(neo4j_driver)

        start = time.time()
        neo4j_load_users(neo4j_driver, users_df)
        neo4j_load_stations(neo4j_driver, stations_df)
        neo4j_load_trips(neo4j_driver, trips_df)
        load_performed(neo4j_driver, trips_df)
        load_starts_at(neo4j_driver, trips_df)
        load_ends_at(neo4j_driver, trips_df)
        save_result(n_users, n_trips, events_per_trip, "neo4j", "load", time.time() - start)

        start = time.time()
        neo4j_q1(neo4j_driver, 1)
        save_result(n_users, n_trips, events_per_trip, "neo4j", "query1", time.time() - start)

        start = time.time()
        neo4j_q2(neo4j_driver)
        save_result(n_users, n_trips, events_per_trip, "neo4j", "query2", time.time() - start)

        print("Neo4j done!")

        # ── Spark Doc (Query 2) ───────────
        print("\n--- Spark Query 2 ---")
        import spark_doc
        spark_doc.client, spark_doc.db = mongo_connect()

        trips_spark = read_from_mongodb()
        users_spark = read_users_from_mongodb()
        trips_spark.cache()
        users_spark.cache()
        trips_spark.count()
        users_spark.count()

        start = time.time()
        result = query2_dataframe(trips_spark, users_spark)
        result.collect()
        save_result(n_users, n_trips, events_per_trip, "spark_doc", "query2", time.time() - start)

        trips_spark.unpersist()
        users_spark.unpersist()
        spark_doc.client.close()
        print("Spark Query 2 done!")

        # ── Spark Graph ───────────────────
        print("\n--- Spark GraphFrames ---")
        graph = build_graph(stations_df, trips_df)
        graph.vertices.cache()
        graph.edges.cache()
        graph.vertices.count()
        graph.edges.count()

        start = time.time()
        run_pagerank(graph)
        save_result(n_users, n_trips, events_per_trip, "spark_graph", "pagerank", time.time() - start)

        start = time.time()
        run_connected_components(graph)
        save_result(n_users, n_trips, events_per_trip, "spark_graph", "connected_components", time.time() - start)

        graph.vertices.unpersist()
        graph.edges.unpersist()
        print("Spark GraphFrames done!")

        # ── Save results after each combination ──
        save_results_to_csv()
        print(f"Combination {idx+1} complete! Results saved.")

    # ── Final cleanup ─────────────────────
    total_time = time.time() - total_start
    neo4j_driver.close()
    spark.stop()
    print("\nAll combinations complete!")
    print(f"Results saved to results.csv")
    print(f"Total execution time: {round(total_time/3600, 2)} hours")