# PostgreSQL Loader for City Mobility Platform

import pg8000
import pandas as pd
from config import POSTGRES_CONFIG

def get_connection():
    conn = pg8000.connect(**POSTGRES_CONFIG)
    return conn

# ── Create Tables ─────────────────────────
def create_tables(conn):
    cursor = conn.cursor()
    
    # Drop existing tables in reverse order due to foreign keys
    cursor.execute("DROP TABLE IF EXISTS events;")
    cursor.execute("DROP TABLE IF EXISTS trips;")
    cursor.execute("DROP TABLE IF EXISTS stations;")
    cursor.execute("DROP TABLE IF EXISTS users;")
    
    # Create fresh tables
    cursor.execute("""
        CREATE TABLE users (
            user_id     INTEGER PRIMARY KEY,
            name        VARCHAR(100),
            surname     VARCHAR(100),
            birthdate   DATE,
            country     VARCHAR(100)
        );
    """)

    cursor.execute("""
        CREATE TABLE stations (
            station_id   INTEGER PRIMARY KEY,
            name         VARCHAR(100),
            city         VARCHAR(100),
            max_capacity INTEGER
        );
    """)

    cursor.execute("""
        CREATE TABLE trips (
            trip_id          INTEGER PRIMARY KEY,
            user_id          INTEGER REFERENCES users(user_id),
            start_station_id INTEGER REFERENCES stations(station_id),
            end_station_id   INTEGER REFERENCES stations(station_id),
            start_time       TIMESTAMP,
            end_time         TIMESTAMP,
            total_cost       NUMERIC(6,2)
        );
    """)

    cursor.execute("""
        CREATE TABLE events (
            event_id  INTEGER PRIMARY KEY,
            trip_id   INTEGER REFERENCES trips(trip_id),
            timestamp TIMESTAMP,
            type      VARCHAR(20),
            value     NUMERIC(6,2)
        );
    """)

    conn.commit()
    print("Tables created successfully!")
    return cursor

# ── Load Users ────────────────────────────
def load_users(conn, cursor, users_df):
    rows = [tuple(row) for row in users_df.itertuples(index=False)]
    cursor.executemany("""
        INSERT INTO users (user_id, name, surname, birthdate, country)
        VALUES (%s, %s, %s, %s, %s)
    """, rows)
    conn.commit()
    print(f"Loaded {len(rows)} users!")


# ── Load Stations ─────────────────────────
def load_stations(conn, cursor, stations_df):
    rows = [tuple(row) for row in stations_df.itertuples(index=False)]
    cursor.executemany("""
        INSERT INTO stations (station_id, name, city, max_capacity)
        VALUES (%s, %s, %s, %s)
    """, rows)
    conn.commit()
    print(f"Loaded {len(rows)} stations!")


# ── Load Trips ────────────────────────────
def load_trips(conn, cursor, trips_df):
    rows = [tuple(row) for row in trips_df.itertuples(index=False)]
    cursor.executemany("""
        INSERT INTO trips (trip_id, user_id, start_station_id, end_station_id,
                          start_time, end_time, total_cost)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, rows)
    conn.commit()
    print(f"Loaded {len(rows)} trips!")


# ── Load Events ───────────────────────────
def load_events(conn, cursor, events_df):
    if events_df.empty:
        print("No events to load!")
        return
    rows = [tuple(row) for row in events_df.itertuples(index=False)]
    cursor.executemany("""
        INSERT INTO events (event_id, trip_id, timestamp, type, value)
        VALUES (%s, %s, %s, %s, %s)
    """, rows)
    conn.commit()
    print(f"Loaded {len(rows)} events!")

# Important point — itertuples(index=False):
# This is the most efficient way to iterate through a Pandas DataFrame. 
# It converts each row into a tuple — exactly what executemany needs. 
# index=False means we don't include the DataFrame index in the tuple.


# -- Main block --------------------
if __name__ == "__main__":
    from generator import generate_all
    
    # Generate all data in one call
    users_df, stations_df, trips_df, events_df = generate_all()
    
    # Connect and load
    print("Connecting to PostgreSQL...")
    conn   = get_connection()
    cursor = create_tables(conn)
    
    print("Loading data...")
    load_users(conn, cursor, users_df)
    load_stations(conn, cursor, stations_df)
    load_trips(conn, cursor, trips_df)
    load_events(conn, cursor, events_df)
    
    # Close connection
    cursor.close()
    conn.close()
    print("PostgreSQL loading complete!")