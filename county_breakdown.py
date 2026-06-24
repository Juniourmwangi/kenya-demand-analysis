import time
import pandas as pd
import psycopg2
from pytrends.request import TrendReq
from sqlalchemy import create_engine
from config import DB_CONFIG

engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ─────────────────────────────────────────
# Strategy: Search keyword + city name
# This is more reliable than region API
# ─────────────────────────────────────────
cities = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"]

keyword_groups = [
    {"category": "Electronics", "keyword": "laptops"},
    {"category": "Finance",     "keyword": "Mpesa"},
    {"category": "Real Estate", "keyword": "land for sale"},
    {"category": "Agriculture", "keyword": "fertilizer"},
    {"category": "Food",        "keyword": "supermarket"},
    {"category": "Health",      "keyword": "hospital"},
    {"category": "Fashion",     "keyword": "clothes online"},
    {"category": "Beauty",      "keyword": "salon"},
]

print("Connecting to Google Trends for City Comparison...")
pytrends = TrendReq(hl='en-KE', tz=180)

all_data = []

for group in keyword_groups:
    category = group["category"]
    base_kw  = group["keyword"]

    # Build city-specific keywords
    city_keywords = [f"{base_kw} {city}" for city in cities]

    print(f"   Pulling: {category} — {base_kw}...")

    try:
        pytrends.build_payload(
            kw_list  = city_keywords,
            geo      = "KE",
            timeframe= "today 12-m"
        )

        df = pytrends.interest_over_time()

        if df.empty:
            print(f"   No data for {category}, skipping...")
            continue

        df.drop(columns=["isPartial"], inplace=True)

        # Average interest per city keyword
        avg_interest = df.mean().reset_index()
        avg_interest.columns = ["keyword", "avg_interest"]
        avg_interest["category"] = category
        avg_interest["base_keyword"] = base_kw

        # Extract city name from keyword
        for city in cities:
            avg_interest.loc[
                avg_interest["keyword"].str.contains(city),
                "county"
            ] = city

        all_data.append(avg_interest)
        print(f"   OK {category} pulled!")
        time.sleep(3)

    except Exception as e:
        print(f"   ERR {category}: {e}")
        time.sleep(10)
        continue

# ─────────────────────────────────────────
# Combine & Save
# ─────────────────────────────────────────
if all_data:
    df_final = pd.concat(all_data, ignore_index=True)
    df_final = df_final.dropna(subset=["county"])
    df_final["interest"] = df_final["avg_interest"].round(1)
    df_final = df_final[["county","keyword","interest","category"]]

    print(f"\nTotal rows ready: {len(df_final)}")
    print(df_final.head(10))

    conn   = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE county_trends;")

    for _, row in df_final.iterrows():
        cursor.execute("""
            INSERT INTO county_trends (county, keyword, interest, category)
            VALUES (%s, %s, %s, %s)
        """, (row["county"], row["keyword"],
              float(row["interest"]), row["category"]))

    conn.commit()
    cursor.close()
    conn.close()
    print(f"Saved {len(df_final)} rows!")

# ─────────────────────────────────────────
# SQL Analysis
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("   KENYA CITY-LEVEL DEMAND ANALYSIS")
print("=" * 60)

conn = engine.connect()

# Query 1: Overall demand per city
q1 = """
    SELECT
        county AS city,
        ROUND(AVG(interest), 1) AS avg_interest,
        COUNT(DISTINCT category) AS categories
    FROM county_trends
    WHERE interest > 0
    GROUP BY county
    ORDER BY avg_interest DESC;
"""
print("\nOVERALL DEMAND PER CITY")
print("-" * 60)
print(pd.read_sql(q1, conn).to_string(index=False))

# Query 2: City leader per category
q2 = """
    SELECT
        category,
        county AS top_city,
        ROUND(MAX(interest), 1) AS interest
    FROM county_trends
    WHERE interest > 0
    GROUP BY category, county
    ORDER BY category, interest DESC;
"""
print("\nDEMAND PER CATEGORY PER CITY")
print("-" * 60)
print(pd.read_sql(q2, conn).to_string(index=False))

# Query 3: Nairobi vs all
q3 = """
    SELECT
        category,
        MAX(CASE WHEN county='Nairobi' THEN interest END) AS Nairobi,
        MAX(CASE WHEN county='Mombasa' THEN interest END) AS Mombasa,
        MAX(CASE WHEN county='Kisumu'  THEN interest END) AS Kisumu,
        MAX(CASE WHEN county='Nakuru'  THEN interest END) AS Nakuru,
        MAX(CASE WHEN county='Eldoret' THEN interest END) AS Eldoret
    FROM county_trends
    GROUP BY category
    ORDER BY Nairobi DESC NULLS LAST;
"""
print("\nNAIROBI vs MOMBASA vs KISUMU vs NAKURU vs ELDORET")
print("-" * 60)
print(pd.read_sql(q3, conn).to_string(index=False))

conn.close()
engine.dispose()
print("\nCity Analysis Complete!")