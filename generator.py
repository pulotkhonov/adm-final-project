# Data Generator for City Mobility Platform with Pandas-based 
import pandas as pd
import random
from faker import Faker
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# ── Scale Parameters ──────────────────────
NUM_USERS        = 1000
NUM_STATIONS     = 50
NUM_TRIPS        = 10000
EVENTS_PER_TRIP  = 2

# ── Italian Cities ────────────────────────
ITALIAN_CITIES = [
    "Rome", "Milan", "Naples", "Turin", "Bologna",
    "Florence", "Venice", "Genoa", "Palermo", "Bari"
]

# ── Event Types ───────────────────────────
EVENT_TYPES = ["GPS", "ERROR", "BATTERY", "DELAY"]

# ── Generate Users ────────────────────────
def generate_users(n):
    data = [{
        "user_id": i,
        "name": fake.first_name(),
        "surname": fake.last_name(),
        "birthdate": fake.date_of_birth(minimum_age=18, maximum_age=70).strftime("%Y-%m-%d"),
        "country": fake.country()
    } for i in range(1, n + 1)]
    
    return pd.DataFrame(data)

# ── Generate Stations ─────────────────────
def generate_stations(n):
    data = [{
        "station_id": i,
        "name": "Station_" + str(i),
        "city": random.choice(ITALIAN_CITIES),
        "max_capacity": random.randint(10, 50)
    } for i in range(1, n + 1)]
    
    return pd.DataFrame(data)

# Important point — list comprehension:
# Notice I am using list comprehension [{...} for i in range(...)] instead of a for loop with append(). 
# This is more efficient and cleaner in Python — it builds the entire list in one step rather than growing it gradually.

# ── Generate Trips ────────────────────────
def generate_trips(n, users_df, stations_df):
    # Convert to lists for random sampling
    user_ids = users_df["user_id"].tolist()
    station_ids = stations_df["station_id"].tolist()
    
    data = []
    for i in range(1, n + 1):
        start_time = fake.date_time_between(start_date="-1y", end_date="now")
        duration = timedelta(minutes=random.randint(5, 120))
        end_time = start_time + duration
        
        data.append({
            "trip_id": i,
            "user_id": random.choice(user_ids),
            "start_station_id": random.choice(station_ids),
            "end_station_id": random.choice(station_ids),
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_cost": round(random.uniform(0.5, 20.0), 2)
        })
    
    return pd.DataFrame(data)
# The problem is start_time and end_time are dependent — end_time needs start_time to be calculated first. 
# But in list comprehension everything is written in one expression, so you can't create start_time and then immediately use it to calculate end_time in the same line.

# ── Generate Events ───────────────────────
def generate_events(trips_df, events_per_trip):
    data = []
    event_id = 1
    
    for _, trip in trips_df.iterrows():
        for _ in range(events_per_trip):
            # Event timestamp must be between trip start and end time
            event_time = fake.date_time_between(
                start_date=datetime.strptime(trip["start_time"], "%Y-%m-%d %H:%M:%S"),
                end_date=datetime.strptime(trip["end_time"], "%Y-%m-%d %H:%M:%S")
            )
            data.append({
                "event_id": event_id,
                "trip_id": int(trip["trip_id"]),
                "timestamp": event_time.strftime("%Y-%m-%d %H:%M:%S"),
                "type": random.choice(EVENT_TYPES),
                "value": round(random.uniform(0.0, 100.0), 2)
            })
            event_id += 1
    
    return pd.DataFrame(data) if data else pd.DataFrame(
        columns=["event_id", "trip_id", "timestamp", "type", "value"]
    )
#Important point — iterrows():
#This is how you loop through a Pandas DataFrame row by row. 
# It returns two things — _ is the row index (we don't need it, hence _) 
# and trip is the actual row data as a dictionary-like object.
#When events_per_trip = 0, the data list will be empty. Creating a DataFrame from an empty list causes problems later. So we return an empty DataFrame with correct column names instead.
#This is a critical edge case that would cause bugs later without this check!

# ── Generate All Data ─────────────────────
def generate_all(n_users=NUM_USERS, n_stations=NUM_STATIONS, 
                 n_trips=NUM_TRIPS, events_per_trip=EVENTS_PER_TRIP):
    
    print("Generating users...")
    users_df = generate_users(n_users)
    
    print("Generating stations...")
    stations_df = generate_stations(n_stations)
    
    print("Generating trips...")
    trips_df = generate_trips(n_trips, users_df, stations_df)
    
    print("Generating events...")
    events_df = generate_events(trips_df, events_per_trip)
    
    print(f"Generated: {len(users_df)} users, {len(stations_df)} stations, "
          f"{len(trips_df)} trips, {len(events_df)} events")
    
    return users_df, stations_df, trips_df, events_df

# ── Main Block ────────────────────────────
if __name__ == "__main__":
    users_df, stations_df, trips_df, events_df = generate_all()
    
    print("\n--- Users Preview ---")
    print(users_df.head(3))
    
    print("\n--- Trips Preview ---")
    print(trips_df.head(3))
    
    print("\n--- Events Preview ---")
    print(events_df.head(3))