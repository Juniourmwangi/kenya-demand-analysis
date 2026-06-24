import psycopg2

conn = psycopg2.connect(
    host     = "localhost",
    port     = 5433,
    user     = "postgres",
    password = "NewPassword123",
    database = "postgres"
)

cur = conn.cursor()
cur.execute("SELECT datname FROM pg_database;")
databases = cur.fetchall()

print("Databases found in PostgreSQL:")
for db in databases:
    print(f"  - {db[0]}")

cur.close()
conn.close()