import psycopg2
from config import DB_CONFIG

try:
    # Attempt connection
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Test query
    cursor.execute("SELECT version();")
    db_version = cursor.fetchone()

    print("✅ Connected to PostgreSQL successfully!")
    print(f"📦 Database : kenya_demand_analysis")
    print(f"🖥️  Version  : {db_version[0]}")

    cursor.close()
    conn.close()
    print("🔒 Connection closed cleanly.")

except Exception as e:
    print(f"❌ Connection failed!")
    print(f"Error: {e}")