# ─────────────────────────────────────────
# Database Configuration
# ─────────────────────────────────────────

# ── PostgreSQL ────────────────────────────
POSTGRES_CONFIG = {
    "host": "localhost",
    "database": "mobility_db",
    "user": "postgres",
    "password": "2108",  
    "port": 5432
}

# ── MongoDB ───────────────────────────────
MONGO_URI = "mongodb://localhost:27017/"
MONGO_DB  = "mobility_db"

# ── Neo4j ─────────────────────────────────
NEO4J_URI      = "bolt://localhost:7687"
NEO4J_USER     = "neo4j"
NEO4J_PASSWORD = "mobility123"  
NEO4J_DB = "citymobility"  