import sqlite3

DB_FILE = "sensor_data.db"

def extract_and_analyze():
    # 1. Connect and pull data once
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    try:
        # Fetch only the last 10 rows in a single retrieval step
        query = "SELECT id, timestamp, distance_cm FROM distance_logs ORDER BY id DESC LIMIT 10"
        cursor.execute(query)
        rows = cursor.fetchall() 
        conn.close() # Close immediately since we have our data
        
        if not rows:
            print("The database is currently empty. Run the sensor script first!")
            return

        # 2. Display the rows
        print("=============================================")
        print("          LAST 10 SENSOR READINGS            ")
        print("=============================================")
        print(f"{'ID':<6} | {'Timestamp':<20} | {'Distance':<12}")
        print("-" * 44)
        
        distances = []
        for row in rows:
            print(f"{row[0]:<6} | {row[1]:<20} | {row[2]:.2f} cm")
            distances.append(row[2]) # Save distances to a list for math

        # 3. Perform statistics in Python memory (No more SQL queries needed!)
        total_count = len(distances)
        avg_distance = sum(distances) / total_count
        min_distance = min(distances)
        max_distance = max(distances)

        print("\n=============================================")
        print("       STATISTICS ON THESE 10 READINGS       ")
        print("=============================================")
        print(f" -> Sample Size:        {total_count} readings")
        print(f" -> Average Distance:   {avg_distance:.2f} cm")
        print(f" -> Closest Object:     {min_distance:.2f} cm")
        print(f" -> Furthest Object:    {max_distance:.2f} cm")

    except sqlite3.OperationalError:
        print("Error: Could not access 'sensor_data.db'. Check if the file exists.")

if __name__ == "__main__":
    extract_and_analyze()