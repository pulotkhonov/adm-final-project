# ─────────────────────────────────────────
# MongoDB Loader for City Mobility Platform
# Pandas-based version
# ─────────────────────────────────────────

from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB

# ── Database Connection ───────────────────
def get_connection():
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    return client, db

# ── Load Users ────────────────────────────
def load_users(db, users_df):
    db.users.drop()  # clear existing data
    records = users_df.to_dict("records")
    db.users.insert_many(records)
    db.users.create_index("user_id")
    print(f"Loaded {len(records)} users!")


# ── Load Trips with Embedded Stations and Events ──
# ── Load Trips with Embedded Stations and Events ──
def load_trips(db, trips_df, stations_df, events_df):
    db.trips.drop()  # clear existing data
    
    # Build station lookup dictionary from DataFrame
    stations_dict = stations_df.set_index("station_id").to_dict("index")
    
    # Build events lookup dictionary using groupby — much faster than iterrows
    events_dict = {}
    if not events_df.empty:
        # Group events by trip_id efficiently
        for trip_id, group in events_df.groupby("trip_id"):
            events_dict[int(trip_id)] = group[
                ["event_id", "timestamp", "type", "value"]
            ].to_dict("records")
    
    # Build embedded trip documents
    trips = []
    for _, trip in trips_df.iterrows():
        trip_id = int(trip["trip_id"])
        start_id = int(trip["start_station_id"])
        end_id = int(trip["end_station_id"])
        
        trips.append({
            "trip_id": trip_id,
            "user_id": int(trip["user_id"]),
            "start_station": stations_dict[start_id],
            "end_station": stations_dict[end_id],
            "start_time": trip["start_time"],
            "end_time": trip["end_time"],
            "total_cost": float(trip["total_cost"]),
            "events": events_dict.get(trip_id, [])
        })
    
    db.trips.insert_many(trips)
    db.trips.create_index("user_id")
    print(f"Loaded {len(trips)} trips!")


    # ── Main Block ────────────────────────────
if __name__ == "__main__":
    from generator import generate_all
    
    # Generate all data in one call
    users_df, stations_df, trips_df, events_df = generate_all()
    
    # Connect to MongoDB
    print("Connecting to MongoDB...")
    client, db = get_connection()
    
    # Load data
    print("Loading data...")
    load_users(db, users_df)
    load_trips(db, trips_df, stations_df, events_df)
    
    # Close connection
    client.close()
    print("Connection closed.")
    print("MongoDB loading complete!")