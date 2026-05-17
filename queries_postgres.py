
import pg8000
from config import POSTGRES_CONFIG

# ── Database Connection ───────────────────
# Connection will be passed as parameter from main.py

# ── Query 1: All trips with user info and start and end station names 
def query1(cursor):
    cursor.execute("""
        SELECT 
            t.trip_id,
            u.name,
            u.surname,
            u.country,
            s1.name AS start_station,
            s2.name AS end_station,
            t.start_time,
            t.end_time,
            t.total_cost
        FROM trips t
        JOIN users u ON t.user_id = u.user_id
        JOIN stations s1 ON t.start_station_id = s1.station_id
        JOIN stations s2 ON t.end_station_id = s2.station_id
    """)
    
    results = cursor.fetchall()
    print(f"Query 1: Found {len(results)} trips")
    return results

# ── Query 2: All users with number of trips and average duration ───
def query2(cursor):
    cursor.execute("""
        SELECT 
            u.user_id,
            u.name,
            u.surname,
            COUNT(t.trip_id) AS num_trips,
            AVG(EXTRACT(EPOCH FROM (t.end_time - t.start_time)) / 60) AS avg_duration_minutes
        FROM users u
        LEFT JOIN trips t ON u.user_id = t.user_id
        GROUP BY u.user_id, u.name, u.surname
    """)
    # I used LEFT JOIN to return all users including those with zero trips, simple JOIN returns the users with at least one trip.
    # Count counts the total number of trips per user 
    # AVG used to calculate average duration of trips in mins
    # EXTRACT(EPOCH)- is used to get the duration in seconds, then divided by 60 to convert to minutes.
    results = cursor.fetchall()
    print(f"Query 2: Found {len(results)} users")
    return results

# ── Query 3: All stations with number of trips starting and ending there 
def query3(cursor):
    cursor.execute("""
        SELECT 
            s.station_id,
            s.name,
            s.city,
            (SELECT COUNT(*) FROM trips t1 
             WHERE t1.start_station_id = s.station_id) AS trips_starting,
            (SELECT COUNT(*) FROM trips t2 
             WHERE t2.end_station_id = s.station_id) AS trips_ending
        FROM stations s
    """)
    
    results = cursor.fetchall()
    print(f"Query 3: Found {len(results)} stations")
    return results

# ── Query 4: All trips with at least one ERROR event ───
def query4(cursor):
    cursor.execute("""
        SELECT DISTINCT
            t.trip_id,
            u.name,
            u.surname,
            s1.name AS start_station,
            s2.name AS end_station,
            t.start_time,
            t.end_time,
            t.total_cost
        FROM trips t
        JOIN users u ON t.user_id = u.user_id
        JOIN stations s1 ON t.start_station_id = s1.station_id
        JOIN stations s2 ON t.end_station_id = s2.station_id
        JOIN events e ON t.trip_id = e.trip_id
        WHERE e.type = 'ERROR'
    """)
    
    results = cursor.fetchall()
    print(f"Query 4: Found {len(results)} trips with ERROR events")
    return results
#Without DISTINCT, the same trip would appear multiple times in results — once per ERROR event, DISTINCT ensures each trip appears only once

# ── Main Block 
if __name__ == "__main__":
    conn = pg8000.connect(**POSTGRES_CONFIG)
    cursor = conn.cursor()
    
    print("\n--- Query 1: All trips with user and station info ---")
    q1 = query1(cursor)
    print(q1[:3])
    
    print("\n--- Query 2: All users with trip count and avg duration ---")
    q2 = query2(cursor)
    print(q2[:3])
    
    print("\n--- Query 3: All stations with trip counts ---")
    q3 = query3(cursor)
    print(q3[:3])
    
    print("\n--- Query 4: Trips with ERROR events ---")
    q4 = query4(cursor)
    print(q4[:3])
    
    cursor.close()
    conn.close()
    print("\nConnection closed.")