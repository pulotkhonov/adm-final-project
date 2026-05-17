# ─────────────────────────────────────────
# Neo4j Queries for City Mobility Platform
# ─────────────────────────────────────────

from neo4j import GraphDatabase
from config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DB

# ── Query 1: All stations reachable by a given user ──
def query1(driver, user_id):
    with driver.session(database=NEO4J_DB) as session:
        results = session.run("""
            MATCH (u:USER {user_id: $user_id})-[:PERFORMED]->
                  (t:TRIP)-[:STARTS_AT|ENDS_AT]->(s:STATION)
            RETURN DISTINCT s.name AS station_name, 
                            s.city AS city
        """, user_id=user_id)
        
        results = [dict(r) for r in results]
        print(f"Query 1: Found {len(results)} reachable stations for user {user_id}")
        return results
    
# ── Query 2: Top 3 most important stations ──
def query2(driver):
    with driver.session(database=NEO4J_DB) as session:
        results = session.run("""
            MATCH (s:STATION)
            WITH s,
                 COUNT {(s)<-[:STARTS_AT]-()} AS trips_starting,
                 COUNT {(s)<-[:ENDS_AT]-()} AS trips_ending
            RETURN s.name AS station_name,
                   s.city AS city,
                   trips_starting,
                   trips_ending,
                   trips_starting + trips_ending AS total_trips
            ORDER BY total_trips DESC
            LIMIT 3
        """)
        
        results = [dict(r) for r in results]
        print(f"Query 2: Top 3 most important stations:")
        for r in results:
            print(f"  {r['station_name']} ({r['city']}) - "
                  f"Starting: {r['trips_starting']}, "
                  f"Ending: {r['trips_ending']}, "
                  f"Total: {r['total_trips']}")
        return results
# ── Main Block ────────────────────────────
if __name__ == "__main__":
    
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    print("\n--- Query 1: Stations reachable by user 1 ---")
    q1 = query1(driver,1)  # test with user_id = 1
    print(q1[:3])
    
    print("\n--- Query 2: Top 3 most important stations ---")
    q2 = query2(driver)
    
    driver.close()
    print("\nConnection closed.")