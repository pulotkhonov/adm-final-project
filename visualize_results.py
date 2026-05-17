# ─────────────────────────────────────────
# Visualization Script for ADM Project Report
# City Mobility Platform - Performance Analysis
# ─────────────────────────────────────────

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import os

# ── Load Data ─────────────────────────────
df = pd.read_csv("results.csv")

# ── Output folder ─────────────────────────
os.makedirs("report_charts", exist_ok=True)

# ── Style Settings ────────────────────────
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 11,
    "legend.fontsize": 10,
    "figure.dpi": 150,
    "axes.grid": True,
    "grid.alpha": 0.3
})

COLORS = {
    "postgres": "#1f77b4",   # blue
    "mongodb":  "#d62728",   # red
    "neo4j":    "#2ca02c",   # green
    "spark_doc":"#ff7f0e",   # orange
    "spark_graph_pr": "#9467bd",  # purple
    "spark_graph_cc": "#8c564b",  # brown
}

TRIP_LABELS = {10000: "10k", 50000: "50k", 100000: "100k"}
USER_LABELS = {1000: "1k", 10000: "10k", 50000: "50k"}

# ─────────────────────────────────────────
# CHART 1: PostgreSQL vs MongoDB — All 4 Queries by Trip Count
# ─────────────────────────────────────────
def chart_pg_vs_mongo_queries():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Part 1.2 — PostgreSQL vs MongoDB: Query Execution Time (seconds)", fontsize=14, fontweight="bold")

    queries = [
        ("query1", "query1_lookup", "Q1: All trips with user & station info"),
        ("query2", "query2",        "Q2: Users with trip count & avg duration"),
        ("query3", "query3",        "Q3: Stations with trips starting/ending"),
        ("query4", "query4",        "Q4: Trips with at least one ERROR event"),
    ]

    trip_vals = [10000, 50000, 100000]
    x = np.arange(len(trip_vals))
    width = 0.35

    for ax, (pg_q, mg_q, title) in zip(axes.flat, queries):
        pg_times = [df[(df["db"]=="postgres") & (df["query"]==pg_q) & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]
        mg_times = [df[(df["db"]=="mongodb")  & (df["query"]==mg_q) & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]

        bars1 = ax.bar(x - width/2, pg_times, width, label="PostgreSQL", color=COLORS["postgres"], alpha=0.85)
        bars2 = ax.bar(x + width/2, mg_times, width, label="MongoDB",    color=COLORS["mongodb"],  alpha=0.85)

        ax.set_title(title)
        ax.set_xlabel("Number of Trips")
        ax.set_ylabel("Time (seconds)")
        ax.set_xticks(x)
        ax.set_xticklabels([TRIP_LABELS[t] for t in trip_vals])
        ax.legend()

        # Add value labels on bars
        for bar in bars1:
            h = bar.get_height()
            ax.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0,3), textcoords="offset points", ha="center", fontsize=8)
        for bar in bars2:
            h = bar.get_height()
            ax.annotate(f"{h:.2f}", xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0,3), textcoords="offset points", ha="center", fontsize=8)

    plt.tight_layout()
    plt.savefig("report_charts/chart1_pg_vs_mongo_queries.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 1 saved: PostgreSQL vs MongoDB queries")

# ─────────────────────────────────────────
# CHART 2: Scalability — Line charts per query
# ─────────────────────────────────────────
def chart_scalability_lines():
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Part 1.2 — Scalability: Query Execution Time vs Number of Trips", fontsize=14, fontweight="bold")

    queries = [
        ("query1", "query1_lookup", "Q1: All trips with user & station info"),
        ("query2", "query2",        "Q2: Users with trip count & avg duration"),
        ("query3", "query3",        "Q3: Stations with trips starting/ending"),
        ("query4", "query4",        "Q4: Trips with at least one ERROR event"),
    ]

    trip_vals = [10000, 50000, 100000]

    for ax, (pg_q, mg_q, title) in zip(axes.flat, queries):
        pg_times = [df[(df["db"]=="postgres") & (df["query"]==pg_q) & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]
        mg_times = [df[(df["db"]=="mongodb")  & (df["query"]==mg_q) & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]

        ax.plot(trip_vals, pg_times, marker="o", label="PostgreSQL", color=COLORS["postgres"], linewidth=2)
        ax.plot(trip_vals, mg_times, marker="s", label="MongoDB",    color=COLORS["mongodb"],  linewidth=2, linestyle="--")

        ax.set_title(title)
        ax.set_xlabel("Number of Trips")
        ax.set_ylabel("Time (seconds)")
        ax.set_xticks(trip_vals)
        ax.set_xticklabels([TRIP_LABELS[t] for t in trip_vals])
        ax.legend()

    plt.tight_layout()
    plt.savefig("report_charts/chart2_scalability_lines.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 2 saved: Scalability line charts")

# ─────────────────────────────────────────
# CHART 3: Loading Time Comparison
# ─────────────────────────────────────────
def chart_loading_times():
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Loading Time Comparison Across Databases", fontsize=14, fontweight="bold")

    trip_vals = [10000, 50000, 100000]
    x = np.arange(len(trip_vals))
    width = 0.25

    pg_load = [df[(df["db"]=="postgres") & (df["query"]=="load") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]
    mg_load = [df[(df["db"]=="mongodb")  & (df["query"]=="load") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]
    n4_load = [df[(df["db"]=="neo4j")    & (df["query"]=="load") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]

    ax.bar(x - width, pg_load, width, label="PostgreSQL", color=COLORS["postgres"], alpha=0.85)
    ax.bar(x,         mg_load, width, label="MongoDB",    color=COLORS["mongodb"],  alpha=0.85)
    ax.bar(x + width, n4_load, width, label="Neo4j",      color=COLORS["neo4j"],    alpha=0.85)

    ax.set_xlabel("Number of Trips")
    ax.set_ylabel("Loading Time (seconds)")
    ax.set_xticks(x)
    ax.set_xticklabels([TRIP_LABELS[t] for t in trip_vals])
    ax.legend()

    plt.tight_layout()
    plt.savefig("report_charts/chart3_loading_times.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 3 saved: Loading times")

# ─────────────────────────────────────────
# CHART 4: Spark Q2 vs MongoDB Q2 — Crossover
# ─────────────────────────────────────────
def chart_spark_vs_mongo_q2():
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Part 1.4 — Spark Q2 vs MongoDB Q2: Execution Time by Trip Count", fontsize=14, fontweight="bold")

    trip_vals = [10000, 50000, 100000]

    spark_times = [df[(df["db"]=="spark_doc") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]
    mongo_times = [df[(df["db"]=="mongodb") & (df["query"]=="query2") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]
    pg_times    = [df[(df["db"]=="postgres") & (df["query"]=="query2") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]

    ax.plot(trip_vals, spark_times, marker="D", label="Spark DataFrame", color=COLORS["spark_doc"],  linewidth=2)
    ax.plot(trip_vals, mongo_times, marker="s", label="MongoDB native",  color=COLORS["mongodb"],    linewidth=2, linestyle="--")
    ax.plot(trip_vals, pg_times,    marker="o", label="PostgreSQL",      color=COLORS["postgres"],   linewidth=2, linestyle="-.")

    ax.set_xlabel("Number of Trips")
    ax.set_ylabel("Time (seconds)")
    ax.set_xticks(trip_vals)
    ax.set_xticklabels([TRIP_LABELS[t] for t in trip_vals])
    ax.legend()

    # Annotate crossover
    ax.annotate("Spark starts\noutperforming MongoDB", xy=(50000, spark_times[1]),
                xytext=(60000, spark_times[1]+0.5),
                arrowprops=dict(arrowstyle="->", color="black"), fontsize=9)

    plt.tight_layout()
    plt.savefig("report_charts/chart4_spark_vs_mongo_q2.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 4 saved: Spark vs MongoDB Q2")

# ─────────────────────────────────────────
# CHART 5: Neo4j Query Times
# ─────────────────────────────────────────
def chart_neo4j_queries():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Part 2.2.1 — Neo4j Query Execution Time", fontsize=14, fontweight="bold")

    trip_vals = [10000, 50000, 100000]

    q1_times = [df[(df["db"]=="neo4j") & (df["query"]=="query1") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]
    q2_times = [df[(df["db"]=="neo4j") & (df["query"]=="query2") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]

    axes[0].plot(trip_vals, q1_times, marker="o", color=COLORS["neo4j"], linewidth=2)
    axes[0].set_title("Q1: Reachable Stations for User")
    axes[0].set_xlabel("Number of Trips")
    axes[0].set_ylabel("Time (seconds)")
    axes[0].set_xticks(trip_vals)
    axes[0].set_xticklabels([TRIP_LABELS[t] for t in trip_vals])

    axes[1].plot(trip_vals, q2_times, marker="s", color=COLORS["neo4j"], linewidth=2)
    axes[1].set_title("Q2: Top 3 Most Important Stations")
    axes[1].set_xlabel("Number of Trips")
    axes[1].set_ylabel("Time (seconds)")
    axes[1].set_xticks(trip_vals)
    axes[1].set_xticklabels([TRIP_LABELS[t] for t in trip_vals])

    plt.tight_layout()
    plt.savefig("report_charts/chart5_neo4j_queries.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 5 saved: Neo4j queries")

# ─────────────────────────────────────────
# CHART 6: GraphFrames PageRank vs Connected Components
# ─────────────────────────────────────────
def chart_graphframes():
    fig, ax = plt.subplots(figsize=(10, 6))
    fig.suptitle("Part 2.2.2 — Spark GraphFrames: PageRank vs Connected Components", fontsize=14, fontweight="bold")

    trip_vals = [10000, 50000, 100000]

    pr_times = [df[(df["db"]=="spark_graph") & (df["query"]=="pagerank") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]
    cc_times = [df[(df["db"]=="spark_graph") & (df["query"]=="connected_components") & (df["n_trips"]==t)]["time_seconds"].mean() for t in trip_vals]

    x = np.arange(len(trip_vals))
    width = 0.35

    bars1 = ax.bar(x - width/2, pr_times, width, label="PageRank",              color=COLORS["spark_graph_pr"], alpha=0.85)
    bars2 = ax.bar(x + width/2, cc_times, width, label="Connected Components",   color=COLORS["spark_graph_cc"], alpha=0.85)

    for bar in bars1:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}s", xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0,3), textcoords="offset points", ha="center", fontsize=9)
    for bar in bars2:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}s", xy=(bar.get_x() + bar.get_width()/2, h), xytext=(0,3), textcoords="offset points", ha="center", fontsize=9)

    ax.set_xlabel("Number of Trips (edges in graph)")
    ax.set_ylabel("Time (seconds)")
    ax.set_xticks(x)
    ax.set_xticklabels([TRIP_LABELS[t] for t in trip_vals])
    ax.legend()

    plt.tight_layout()
    plt.savefig("report_charts/chart6_graphframes.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 6 saved: GraphFrames")

# ─────────────────────────────────────────
# CHART 7: Events per trip impact on PostgreSQL Q4
# ─────────────────────────────────────────
def chart_events_impact():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("Impact of Events per Trip on Query Performance", fontsize=14, fontweight="bold")

    event_vals = [0, 2, 5, 10]

    # PostgreSQL Q4 — grows with events
    pg_q4 = [df[(df["db"]=="postgres") & (df["query"]=="query4") & (df["events_per_trip"]==e)]["time_seconds"].mean() for e in event_vals]
    axes[0].plot(event_vals, pg_q4, marker="o", color=COLORS["postgres"], linewidth=2)
    axes[0].set_title("PostgreSQL Q4: Trips with ERROR events")
    axes[0].set_xlabel("Events per Trip")
    axes[0].set_ylabel("Time (seconds)")
    axes[0].set_xticks(event_vals)

    # MongoDB Q4 — should stay flat (embedded)
    mg_q4 = [df[(df["db"]=="mongodb") & (df["query"]=="query4") & (df["events_per_trip"]==e)]["time_seconds"].mean() for e in event_vals]
    axes[1].plot(event_vals, pg_q4, marker="o", label="PostgreSQL", color=COLORS["postgres"], linewidth=2)
    axes[1].plot(event_vals, mg_q4, marker="s", label="MongoDB",    color=COLORS["mongodb"],  linewidth=2, linestyle="--")
    axes[1].set_title("Q4 Comparison: PostgreSQL vs MongoDB")
    axes[1].set_xlabel("Events per Trip")
    axes[1].set_ylabel("Time (seconds)")
    axes[1].set_xticks(event_vals)
    axes[1].legend()

    plt.tight_layout()
    plt.savefig("report_charts/chart7_events_impact.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 7 saved: Events impact")

# ─────────────────────────────────────────
# CHART 8: Memory Usage Comparison
# ─────────────────────────────────────────
def chart_memory_usage():
    fig, ax = plt.subplots(figsize=(12, 6))
    fig.suptitle("Memory Usage by Database and Trip Count", fontsize=14, fontweight="bold")

    trip_vals = [10000, 50000, 100000]
    dbs = ["postgres", "mongodb", "neo4j", "spark_doc"]
    labels = ["PostgreSQL", "MongoDB", "Neo4j", "Spark"]
    colors = [COLORS["postgres"], COLORS["mongodb"], COLORS["neo4j"], COLORS["spark_doc"]]

    x = np.arange(len(trip_vals))
    width = 0.2

    for i, (db, label, color) in enumerate(zip(dbs, labels, colors)):
        if db == "spark_doc":
            mem = [df[(df["db"]==db) & (df["n_trips"]==t)]["memory_mb"].mean() for t in trip_vals]
        else:
            mem = [df[(df["db"]==db) & (df["query"]=="load") & (df["n_trips"]==t)]["memory_mb"].mean() for t in trip_vals]
        offset = (i - 1.5) * width
        ax.bar(x + offset, mem, width, label=label, color=color, alpha=0.85)

    ax.set_xlabel("Number of Trips")
    ax.set_ylabel("Memory Usage (MB)")
    ax.set_xticks(x)
    ax.set_xticklabels([TRIP_LABELS[t] for t in trip_vals])
    ax.legend()

    plt.tight_layout()
    plt.savefig("report_charts/chart8_memory_usage.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 8 saved: Memory usage")

# ─────────────────────────────────────────
# CHART 9: Summary heatmap — All queries all DBs
# ─────────────────────────────────────────
def chart_summary_heatmap():
    # Use max scale for summary
    max_scale = df[(df["n_users"]==50000) & (df["n_trips"]==100000) & (df["events_per_trip"]==10)]

    data = {
        "PostgreSQL Q1": max_scale[(max_scale["db"]=="postgres") & (max_scale["query"]=="query1")]["time_seconds"].values[0],
        "PostgreSQL Q2": max_scale[(max_scale["db"]=="postgres") & (max_scale["query"]=="query2")]["time_seconds"].values[0],
        "PostgreSQL Q3": max_scale[(max_scale["db"]=="postgres") & (max_scale["query"]=="query3")]["time_seconds"].values[0],
        "PostgreSQL Q4": max_scale[(max_scale["db"]=="postgres") & (max_scale["query"]=="query4")]["time_seconds"].values[0],
        "MongoDB Q1":    max_scale[(max_scale["db"]=="mongodb") & (max_scale["query"]=="query1_lookup")]["time_seconds"].values[0],
        "MongoDB Q2":    max_scale[(max_scale["db"]=="mongodb") & (max_scale["query"]=="query2")]["time_seconds"].values[0],
        "MongoDB Q3":    max_scale[(max_scale["db"]=="mongodb") & (max_scale["query"]=="query3")]["time_seconds"].values[0],
        "MongoDB Q4":    max_scale[(max_scale["db"]=="mongodb") & (max_scale["query"]=="query4")]["time_seconds"].values[0],
        "Neo4j Q1":      max_scale[(max_scale["db"]=="neo4j") & (max_scale["query"]=="query1")]["time_seconds"].values[0],
        "Neo4j Q2":      max_scale[(max_scale["db"]=="neo4j") & (max_scale["query"]=="query2")]["time_seconds"].values[0],
        "Spark Q2":      max_scale[(max_scale["db"]=="spark_doc")]["time_seconds"].values[0],
        "PageRank":      max_scale[(max_scale["db"]=="spark_graph") & (max_scale["query"]=="pagerank")]["time_seconds"].values[0],
        "Conn. Comp.":   max_scale[(max_scale["db"]=="spark_graph") & (max_scale["query"]=="connected_components")]["time_seconds"].values[0],
    }

    fig, ax = plt.subplots(figsize=(12, 5))
    fig.suptitle("Query Execution Times at Maximum Scale\n(50k users, 100k trips, 10 events/trip)", fontsize=13, fontweight="bold")

    keys = list(data.keys())
    vals = list(data.values())
    colors_list = [COLORS["postgres"]]*4 + [COLORS["mongodb"]]*4 + [COLORS["neo4j"]]*2 + [COLORS["spark_doc"]] + [COLORS["spark_graph_pr"]]*2

    bars = ax.barh(keys, vals, color=colors_list, alpha=0.85)

    for bar, val in zip(bars, vals):
        ax.text(val + 0.1, bar.get_y() + bar.get_height()/2, f"{val:.2f}s", va="center", fontsize=9)

    ax.set_xlabel("Execution Time (seconds)")
    ax.invert_yaxis()

    plt.tight_layout()
    plt.savefig("report_charts/chart9_summary_max_scale.png", bbox_inches="tight")
    plt.close()
    print("✅ Chart 9 saved: Summary at max scale")

# ─────────────────────────────────────────
# PRINT SUMMARY TABLES for report
# ─────────────────────────────────────────
def print_summary_tables():
    print("\n=== SUMMARY TABLE FOR REPORT ===")
    configs = [
        (1000, 10000, 0),
        (1000, 10000, 2),
        (1000, 10000, 5),
        (1000, 10000, 10),
        (10000, 50000, 2),
        (50000, 100000, 5),
        (50000, 100000, 10),
    ]

    rows = []
    for u, t, e in configs:
        sub = df[(df["n_users"]==u) & (df["n_trips"]==t) & (df["events_per_trip"]==e)]
        row = {
            "Config": f"u={u//1000}k, t={t//1000}k, e={e}",
            "PG-Q1": round(sub[(sub["db"]=="postgres") & (sub["query"]=="query1")]["time_seconds"].values[0], 3),
            "PG-Q2": round(sub[(sub["db"]=="postgres") & (sub["query"]=="query2")]["time_seconds"].values[0], 3),
            "PG-Q3": round(sub[(sub["db"]=="postgres") & (sub["query"]=="query3")]["time_seconds"].values[0], 3),
            "PG-Q4": round(sub[(sub["db"]=="postgres") & (sub["query"]=="query4")]["time_seconds"].values[0], 3),
            "MG-Q1": round(sub[(sub["db"]=="mongodb") & (sub["query"]=="query1_lookup")]["time_seconds"].values[0], 3),
            "MG-Q2": round(sub[(sub["db"]=="mongodb") & (sub["query"]=="query2")]["time_seconds"].values[0], 3),
            "MG-Q3": round(sub[(sub["db"]=="mongodb") & (sub["query"]=="query3")]["time_seconds"].values[0], 3),
            "MG-Q4": round(sub[(sub["db"]=="mongodb") & (sub["query"]=="query4")]["time_seconds"].values[0], 3),
        }
        rows.append(row)

    summary = pd.DataFrame(rows)
    print(summary.to_string(index=False))

    print("\n=== SPARK COMPARISON TABLE ===")
    spark_rows = []
    for u, t, e in configs:
        sub = df[(df["n_users"]==u) & (df["n_trips"]==t) & (df["events_per_trip"]==e)]
        row = {
            "Config": f"u={u//1000}k, t={t//1000}k, e={e}",
            "PG-Q2":    round(sub[(sub["db"]=="postgres") & (sub["query"]=="query2")]["time_seconds"].values[0], 3),
            "MG-Q2":    round(sub[(sub["db"]=="mongodb")  & (sub["query"]=="query2")]["time_seconds"].values[0], 3),
            "Spark-Q2": round(sub[(sub["db"]=="spark_doc")]["time_seconds"].values[0], 3),
        }
        spark_rows.append(row)

    spark_summary = pd.DataFrame(spark_rows)
    print(spark_summary.to_string(index=False))

# ─────────────────────────────────────────
# RUN ALL
# ─────────────────────────────────────────
if __name__ == "__main__":
    print("Generating all charts...")
    chart_pg_vs_mongo_queries()
    chart_scalability_lines()
    chart_loading_times()
    chart_spark_vs_mongo_q2()
    chart_neo4j_queries()
    chart_graphframes()
    chart_events_impact()
    chart_memory_usage()
    chart_summary_heatmap()
    print_summary_tables()
    print("\n✅ All charts saved to report_charts/ folder!")
    print("Copy results.csv to your project folder and run: py visualize_results.py")
