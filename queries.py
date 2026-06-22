import pandas as pd
from sqlalchemy import create_engine
from config import DB_CONFIG

# ─────────────────────────────────────────
# Database Connection via SQLAlchemy
# ─────────────────────────────────────────
engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

conn = engine.connect()

print("=" * 60)
print("   KENYA CONSUMER DEMAND ANALYSIS — SQL INSIGHTS")
print("=" * 60)

# ─────────────────────────────────────────────────────────
# QUERY 1: Top 10 Most Searched Products in Kenya
# ─────────────────────────────────────────────────────────
q1 = """
    SELECT
        keyword,
        ROUND(AVG(interest), 1)  AS avg_interest,
        MAX(interest)            AS peak_interest
    FROM search_trends
    WHERE interest > 0
    GROUP BY keyword
    ORDER BY avg_interest DESC
    LIMIT 10;
"""
print("\n📊 TOP 10 MOST SEARCHED PRODUCTS IN KENYA")
print("-" * 60)
print(pd.read_sql(q1, conn).to_string(index=False))

# ─────────────────────────────────────────────────────────
# QUERY 2: Best Performing Category
# ─────────────────────────────────────────────────────────
q2 = """
    SELECT
        CASE
            WHEN keyword IN ('smartphones Kenya','laptops Kenya','TVs Kenya','earphones Kenya','generators Kenya')
                THEN 'Electronics'
            WHEN keyword IN ('clothes online Kenya','sneakers Kenya','handbags Kenya','segunda Kenya','mitumba Kenya')
                THEN 'Fashion'
            WHEN keyword IN ('supermarket Kenya','food delivery Kenya','cooking gas Kenya','unga Kenya','sukuma wiki Kenya')
                THEN 'Food & Grocery'
            WHEN keyword IN ('salon equipment Kenya','wigs Kenya','weaves Kenya','skincare Kenya','perfume Kenya')
                THEN 'Beauty & Salon'
            WHEN keyword IN ('houses for sale Nairobi','land Kenya','bedsitter Nairobi','Airbnb Kenya','rental houses Kenya')
                THEN 'Real Estate'
            WHEN keyword IN ('fertilizer Kenya','seeds Kenya','poultry Kenya','greenhouse Kenya','dairy farming Kenya')
                THEN 'Agriculture'
            WHEN keyword IN ('loans Kenya','Mpesa Kenya','Fuliza Kenya','forex Kenya','crypto Kenya')
                THEN 'Finance'
            WHEN keyword IN ('pharmacy Kenya','hospital Kenya','insurance Kenya','chemist Kenya','dawa Kenya')
                THEN 'Health'
        END AS category,
        ROUND(AVG(interest), 1) AS avg_interest,
        MAX(interest)           AS peak_interest,
        COUNT(*)                AS data_points
    FROM search_trends
    WHERE interest > 0
    GROUP BY category
    ORDER BY avg_interest DESC;
"""
print("\n🏆 DEMAND BY CATEGORY")
print("-" * 60)
print(pd.read_sql(q2, conn).to_string(index=False))

# ─────────────────────────────────────────────────────────
# QUERY 3: Monthly Trend — Which Month Has Highest Demand?
# ─────────────────────────────────────────────────────────
q3 = """
    SELECT
        TO_CHAR(date, 'Mon YYYY')   AS month,
        ROUND(AVG(interest), 1)     AS avg_interest,
        COUNT(DISTINCT keyword)     AS keywords_tracked
    FROM search_trends
    WHERE interest > 0
    GROUP BY TO_CHAR(date, 'Mon YYYY'), DATE_TRUNC('month', date)
    ORDER BY DATE_TRUNC('month', date) ASC;
"""
print("\n📅 MONTHLY DEMAND TRENDS")
print("-" * 60)
print(pd.read_sql(q3, conn).to_string(index=False))

# ─────────────────────────────────────────────────────────
# QUERY 4: Top 5 Peak Demand Moments
# ─────────────────────────────────────────────────────────
q4 = """
    SELECT
        date,
        keyword,
        interest
    FROM search_trends
    ORDER BY interest DESC
    LIMIT 5;
"""
print("\n🔥 TOP 5 PEAK DEMAND MOMENTS")
print("-" * 60)
print(pd.read_sql(q4, conn).to_string(index=False))

# ─────────────────────────────────────────────────────────
# QUERY 5: Rising Products — Last 3 Months vs Previous 3
# ─────────────────────────────────────────────────────────
q5 = """
    SELECT
        keyword,
        ROUND(AVG(CASE WHEN date >= CURRENT_DATE - INTERVAL '3 months'
              THEN interest END), 1) AS recent_avg,
        ROUND(AVG(CASE WHEN date < CURRENT_DATE - INTERVAL '3 months'
              AND date >= CURRENT_DATE - INTERVAL '6 months'
              THEN interest END), 1) AS previous_avg
    FROM search_trends
    WHERE interest > 0
    GROUP BY keyword
    HAVING
        AVG(CASE WHEN date >= CURRENT_DATE - INTERVAL '3 months'
            THEN interest END) IS NOT NULL
        AND
        AVG(CASE WHEN date < CURRENT_DATE - INTERVAL '3 months'
            AND date >= CURRENT_DATE - INTERVAL '6 months'
            THEN interest END) IS NOT NULL
    ORDER BY recent_avg DESC
    LIMIT 10;
"""
print("\n📈 RISING PRODUCTS — RECENT vs PREVIOUS 3 MONTHS")
print("-" * 60)
print(pd.read_sql(q5, conn).to_string(index=False))

# ─────────────────────────────────────────────────────────
# Close Connection
# ─────────────────────────────────────────────────────────
conn.close()
engine.dispose()
print("\n✅ Analysis Complete!")