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
# Competitor Groups — Max 5 per request
# ─────────────────────────────────────────
competitor_groups = [
    {
        "category": "E-Commerce",
        "brands": ["Jumia Kenya", "Kilimall", "Jiji Kenya", "Masoko", "Copia Kenya"]
    },
    {
        "category": "Telecom",
        "brands": ["Safaricom", "Airtel Kenya", "Telkom Kenya", "Faiba", "Zuku"]
    },
    {
        "category": "Banking",
        "brands": ["Equity Bank Kenya", "KCB Kenya", "Cooperative Bank Kenya",
                   "Absa Kenya", "NCBA Kenya"]
    },
    {
        "category": "Betting",
        "brands": ["Sportpesa", "Betin Kenya", "Odibets", "Betika", "Mcheza"]
    },
    {
        "category": "Food Delivery",
        "brands": ["Glovo Kenya", "Uber Eats Kenya", "Bolt Food Kenya",
                   "Little Ride Kenya", "Jumia Food Kenya"]
    },
]

# ─────────────────────────────────────────
# STEP 1: Pull Data from Google Trends
# ─────────────────────────────────────────
print("Connecting to Google Trends...")
pytrends = TrendReq(hl='en-KE', tz=180)

all_data = []

for group in competitor_groups:
    category = group["category"]
    brands   = group["brands"]

    print(f"   Pulling: {category}...")

    try:
        pytrends.build_payload(
            kw_list  = brands,
            geo      = "KE",
            timeframe= "today 12-m"
        )

        df = pytrends.interest_over_time()

        if df.empty:
            print(f"   No data for {category}, skipping...")
            continue

        df.drop(columns=["isPartial"], inplace=True)
        df.reset_index(inplace=True)

        # Melt to long format
        df_melted = df.melt(
            id_vars   = "date",
            var_name  = "brand",
            value_name= "interest"
        )
        df_melted["category"] = category
        df_melted["region"]   = "Kenya"
        df_melted["date"]     = pd.to_datetime(df_melted["date"]).dt.date

        all_data.append(df_melted)
        print(f"   OK {category} pulled!")
        time.sleep(3)

    except Exception as e:
        print(f"   ERR {category}: {e}")
        time.sleep(10)
        continue

# ─────────────────────────────────────────
# STEP 2: Combine & Save to PostgreSQL
# ─────────────────────────────────────────
if all_data:
    df_final = pd.concat(all_data, ignore_index=True)
    print(f"\nTotal rows ready: {len(df_final)}")

    conn   = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Clear old data
    cursor.execute("TRUNCATE TABLE competitor_trends;")

    for _, row in df_final.iterrows():
        cursor.execute("""
            INSERT INTO competitor_trends
                (date, brand, category, interest, region)
            VALUES (%s, %s, %s, %s, %s)
        """, (row["date"], row["brand"],
              row["category"], row["interest"], row["region"]))

    conn.commit()
    cursor.close()
    conn.close()

    print(f"Saved {len(df_final)} rows to competitor_trends table!")

# ─────────────────────────────────────────
# STEP 3: Analyse with SQL
# ─────────────────────────────────────────
print("\n" + "=" * 60)
print("   KENYA COMPETITOR BRAND ANALYSIS")
print("=" * 60)

conn = engine.connect()

# Query 1: Brand Rankings per Category
q1 = """
    SELECT
        category,
        brand,
        ROUND(AVG(interest), 1) AS avg_interest,
        MAX(interest)           AS peak_interest
    FROM competitor_trends
    WHERE interest > 0
    GROUP BY category, brand
    ORDER BY category, avg_interest DESC;
"""
print("\nBRAND RANKINGS PER CATEGORY")
print("-" * 60)
print(pd.read_sql(q1, conn).to_string(index=False))

# Query 2: Overall Brand Winners
q2 = """
    SELECT
        brand,
        category,
        ROUND(AVG(interest), 1) AS avg_interest
    FROM competitor_trends
    WHERE interest > 0
    GROUP BY brand, category
    ORDER BY avg_interest DESC
    LIMIT 10;
"""
print("\nTOP 10 MOST SEARCHED BRANDS IN KENYA")
print("-" * 60)
print(pd.read_sql(q2, conn).to_string(index=False))

# Query 3: Category Market Leaders
q3 = """
    SELECT DISTINCT ON (category)
        category,
        brand        AS market_leader,
        ROUND(AVG(interest) OVER (PARTITION BY category, brand), 1) AS avg_interest
    FROM competitor_trends
    WHERE interest > 0
    ORDER BY category, avg_interest DESC;
"""
print("\nMARKET LEADERS PER CATEGORY")
print("-" * 60)
print(pd.read_sql(q3, conn).to_string(index=False))

conn.close()
engine.dispose()
print("\nCompetitor Analysis Complete!")