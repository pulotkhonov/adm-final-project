# ADM Project 2025/2026 — City Mobility Platform

Multi-database implementation and performance analysis of a city-scale electric vehicle rental platform.

## Technologies
- **PostgreSQL** — relational model
- **MongoDB** — document model
- **Neo4j** — graph model
- **Apache Spark / PySpark / GraphFrames** — distributed processing

## Project Structure

| File | Description |
|------|-------------|
| `config.py` | Database connection settings |
| `generator.py` | Synthetic data generation (Faker) |
| `load_postgres.py` | PostgreSQL data loader |
| `load_mongo.py` | MongoDB data loader |
| `load_neo4j.py` | Neo4j data loader |
| `queries_postgres.py` | PostgreSQL query implementations |
| `queries_mongo.py` | MongoDB query implementations |
| `queries_neo4j.py` | Neo4j Cypher query implementations |
| `spark_doc.py` | Spark DataFrame implementation of Query 2 |
| `spark_graph.py` | Spark GraphFrames — PageRank and Connected Components |
| `main.py` | Main benchmark automation script (all 36 combinations) |
| `results.csv` | Benchmark results |
| `visualize_results.py` | Chart generation from results |
| `ADM_Report_final.html` | Project report (HTML) |
| `ADM_Report_final.pdf` | Project report (PDF) |

## How to Run

### Requirements
- Python 3.11 (required for PySpark compatibility)
- Python 3.14 (for non-Spark scripts)
- PostgreSQL, MongoDB, Neo4j running locally
- Java JDK 8

### Install dependencies
```bash
pip install pymongo pg8000 neo4j faker pandas pyspark
```

### Configure connections
Edit `config.py` with your database credentials.

### Run full benchmark
```bash
python main.py
```

### Run individual loaders
```bash
python load_postgres.py
python load_mongo.py
python load_neo4j.py
```

## Scale Combinations Tested
- Users: 1k, 10k, 50k
- Trips: 10k, 50k, 100k
- Events per trip: 0, 2, 5, 10
- Total: 36 combinations
