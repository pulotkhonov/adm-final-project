# ─────────────────────────────────────────
# MongoDB Queries for City Mobility Platform
# ─────────────────────────────────────────

from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB


def query1_lookup(db):
    results = db.trips.aggregate([
        # step 1 - lookup user info
        {"$lookup": {
            "from": "users",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "user_info"
        }},
        # step 2 - unwind user_info array
        {"$unwind": "$user_info"},
        # step 3 - select which fields to show
        {"$project": {
            "trip_id": 1,
            "user_info.name": 1,
            "user_info.surname": 1,
            "start_station.name": 1,
            "end_station.name": 1,
            "start_time": 1,
            "end_time": 1,
            "total_cost": 1
        }}
    ], allowDiskUse=True) 
    
    results = list(results)
    print(f"Query 1 (lookup): Found {len(results)} trips")
    return results
# Critical point — $unwind:
# $lookup returns user info as an array even if there's only one user. 
# $unwind converts that array into a single object so we can access fields directly.

# ── Query 2: All users with number of trips and average duration ──
def query2(db):
    results = db.users.aggregate([
        # Step 1 - lookup all trips for each user
        {"$lookup": {
            "from": "trips",
            "localField": "user_id",
            "foreignField": "user_id",
            "as": "user_trips"
        }},
        # Step 2 - project fields, count trips and calculate avg duration
        {"$project": {
            "user_id": 1,
            "name": 1,
            "surname": 1,
            # $size counts the number of trips in the array
            "num_trips": {"$size": "$user_trips"},
            # $map calculates duration for each trip, $avg averages them
            "avg_duration_minutes": {"$avg": {
                "$map": {
                    "input": "$user_trips",
                    "as": "trip",
                    "in": {"$divide": [
                        {"$subtract": [
                            {"$toDate": "$$trip.end_time"},
                            {"$toDate": "$$trip.start_time"}
                        ]},
                        60000  # milliseconds to minutes
                    ]}
                }
            }}
        }}
    ])
    
    results = list(results)
    print(f"Query 2: Found {len(results)} users")
    return results

# ── Query 3: All stations with number of trips starting and ending there ──
def query3(db):
    # Count trips starting at each station
    starting = db.trips.aggregate([
        {"$group": {
            "_id": "$start_station.name",
            "city": {"$first": "$start_station.city"},
            "trips_starting": {"$sum": 1}
        }}
    ])
    starting_dict = {s["_id"]: s for s in starting}
    
    # Count trips ending at each station
    ending = db.trips.aggregate([
        {"$group": {
            "_id": "$end_station.name",
            "trips_ending": {"$sum": 1}
        }}
    ])
    ending_dict = {e["_id"]: e for e in ending}
    
    # Combine both results in Python
    results = []
    for station_name, data in starting_dict.items():
        results.append({
            "station_name": station_name,
            "city": data["city"],
            "trips_starting": data["trips_starting"],
            "trips_ending": ending_dict.get(station_name, {}).get("trips_ending", 0)
        })
    
    print(f"Query 3: Found {len(results)} stations")
    return results

# We run two separate aggregations — one grouping by start_station.name, one by end_station.name
# Each gives us counts per station
# We combine them in Python using dictionaries
# ending_dict.get(station_name, {}).get("trips_ending", 0) handles stations with zero ending trips

# ── Query 4: All trips with at least one ERROR event ──
def query4(db):
    results = list(db.trips.find(
        {"events.type": "ERROR"},  # filter trips with ERROR events
        {"trip_id": 1, "user_id": 1, 
         "start_station.name": 1, 
         "end_station.name": 1,
         "start_time": 1, "end_time": 1, 
         "total_cost": 1}  # project only needed fields
    ))
    
    print(f"Query 4: Found {len(results)} trips with ERROR events")
    return results

# ── Main Block ────────────────────────────
if __name__ == "__main__":
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    
    print("\n--- Query 1 (lookup): All trips with user and station info ---")
    q1_lookup = query1_lookup(db)
    print(q1_lookup[:3])
    
    print("\n--- Query 1 (python): All trips with user and station info ---")
    q1_python = query1_python(db)
    print(q1_python[:3])
    
    print("\n--- Query 2: All users with trip count and avg duration ---")
    q2 = query2(db)
    print(q2[:3])
    
    print("\n--- Query 3: All stations with trip counts ---")
    q3 = query3(db)
    print(q3[:3])
    
    print("\n--- Query 4: Trips with ERROR events ---")
    q4 = query4(db)
    print(q4[:3])
    
    client.close()
    print("\nConnection closed.")