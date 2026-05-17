# ─────────────────────────────────────────
# Neo4j Loader for City Mobility Platform
# Pandas-based version with batch processing
# ─────────────────────────────────────────

from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DB

BATCH_SIZE = 2000  # number of records per batch

# ── Database Connection ───────────────────
def get_connection():
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USER, NEO4J_PASSWORD)
    )
    return driver


# ── Clear existing data ───────────────────
def clear_db(driver):
    with driver.session(database=NEO4J_DB) as session:
        session.run("""
            MATCH (n) 
            CALL { WITH n DETACH DELETE n } 
            IN TRANSACTIONS OF 1000 ROWS
        """)
    print("Database cleared!")

def create_indexes(driver):
    with driver.session(database=NEO4J_DB) as session:
        session.run("CREATE INDEX user_id IF NOT EXISTS FOR (u:USER) ON (u.user_id)")
        session.run("CREATE INDEX station_id IF NOT EXISTS FOR (s:STATION) ON (s.station_id)")
        session.run("CREATE INDEX trip_id IF NOT EXISTS FOR (t:TRIP) ON (t.trip_id)")
    print("Indexes created!")

# ── Batch helper function ─────────────────
def batch_insert(driver, query, data, batch_size=BATCH_SIZE):
    total = len(data)
    for i in range(0, total, batch_size):
        batch = data[i:i + batch_size]
        with driver.session(database=NEO4J_DB) as session:
            session.run(query, {"batch": batch})
    print(f"Inserted {total} records in {(total // batch_size) + 1} batches!")


# ── Load User Nodes ───────────────────────
def load_users(driver, users_df):
    data = users_df.to_dict("records")
    query = """
        UNWIND $batch AS row
        CREATE (:USER {
            user_id: row.user_id,
            name: row.name,
            surname: row.surname,
            birthdate: row.birthdate,
            country: row.country
        })
    """
    batch_insert(driver, query, data)
    print(f"Loaded {len(data)} user nodes!")


# ── Load Station Nodes ────────────────────
def load_stations(driver, stations_df):
    data = stations_df.to_dict("records")
    query = """
        UNWIND $batch AS row
        CREATE (:STATION {
            station_id: row.station_id,
            name: row.name,
            city: row.city,
            max_capacity: row.max_capacity
        })
    """
    batch_insert(driver, query, data)
    print(f"Loaded {len(data)} station nodes!")


# ── Load Trip Nodes ───────────────────────
def load_trips(driver, trips_df):
    data = trips_df[["trip_id", "start_time", 
                      "end_time", "total_cost"]].to_dict("records")
    query = """
        UNWIND $batch AS row
        CREATE (:TRIP {
            trip_id: row.trip_id,
            start_time: row.start_time,
            end_time: row.end_time,
            total_cost: row.total_cost
        })
    """
    batch_insert(driver, query, data)
    print(f"Loaded {len(data)} trip nodes!")


# ── Load PERFORMED Relationships ──────────
def load_performed(driver, trips_df):
    data = trips_df[["user_id", "trip_id"]].to_dict("records")
    query = """
        UNWIND $batch AS row
        MATCH (u:USER {user_id: row.user_id})
        MATCH (t:TRIP {trip_id: row.trip_id})
        CREATE (u)-[:PERFORMED]->(t)
    """
    batch_insert(driver, query, data)
    print(f"Loaded {len(data)} PERFORMED relationships!")


# ── Load STARTS_AT Relationships ──────────
def load_starts_at(driver, trips_df):
    data = trips_df[["trip_id", "start_station_id"]].to_dict("records")
    query = """
        UNWIND $batch AS row
        MATCH (t:TRIP {trip_id: row.trip_id})
        MATCH (s:STATION {station_id: row.start_station_id})
        CREATE (t)-[:STARTS_AT]->(s)
    """
    batch_insert(driver, query, data)
    print(f"Loaded {len(data)} STARTS_AT relationships!")


# ── Load ENDS_AT Relationships ────────────
def load_ends_at(driver, trips_df):
    data = trips_df[["trip_id", "end_station_id"]].to_dict("records")
    query = """
        UNWIND $batch AS row
        MATCH (t:TRIP {trip_id: row.trip_id})
        MATCH (s:STATION {station_id: row.end_station_id})
        CREATE (t)-[:ENDS_AT]->(s)
    """
    batch_insert(driver, query, data)
    print(f"Loaded {len(data)} ENDS_AT relationships!")


# ── Main Block ────────────────────────────
if __name__ == "__main__":
    from generator import generate_all

    users_df, stations_df, trips_df, events_df = generate_all()

    print("Connecting to Neo4j...")
    driver = get_connection()

    # Order matters!
    clear_db(driver)          # 1. clear old data
    create_indexes(driver)    # 2. create indexes BEFORE loading
    
    print("Loading nodes...")
    load_users(driver, users_df)
    load_stations(driver, stations_df)
    load_trips(driver, trips_df)

    print("Loading relationships...")
    load_performed(driver, trips_df)
    load_starts_at(driver, trips_df)
    load_ends_at(driver, trips_df)

    driver.close()
    print("Neo4j loading complete!")