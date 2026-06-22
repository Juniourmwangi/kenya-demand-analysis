import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from config import DB_CONFIG

# ─────────────────────────────────────────
# Database Connection
# ─────────────────────────────────────────
engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

print("🎨 Building Kenya Market Demand Charts...")

# ─────────────────────────────────────────
# CHART 1: Top 10 Most Searched Products
# ─────────────────────────────────────────
q1 = """
    SELECT keyword,
           ROUND(AVG(interest), 1) AS avg_interest
    FROM search_trends
    WHERE interest > 0
    GROUP BY keyword
    ORDER BY avg_interest DESC
    LIMIT 10;
"""
df1 = pd.read_sql(q1, engine)
df1["keyword"] = df1["keyword"].str.replace(" Kenya", "").str.replace(" Nairobi", "")

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(df1["keyword"], df1["avg_interest"], color="#2E86AB", edgecolor="white")
ax.set_xlabel("Average Search Interest (0-100)", fontsize=11)
ax.set_title("🇰🇪 Top 10 Most Searched Products in Kenya\n(Jun 2025 — Jun 2026)",
             fontsize=13, fontweight="bold", pad=15)
ax.invert_yaxis()
ax.set_xlim(0, 110)
ax.grid(axis="x", linestyle="--", alpha=0.4)
for bar, val in zip(bars, df1["avg_interest"]):
    ax.text(bar.get_width() + 1, bar.get_y() + bar.get_height() / 2,
            f"{val}", va="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/top10_products.png", dpi=150)
plt.show()
print("✅ Chart 1 saved — Top 10 Products")

# ─────────────────────────────────────────
# CHART 2: Demand by Category
# ─────────────────────────────────────────
q2 = """
    SELECT
        CASE
            WHEN keyword IN ('smartphones Kenya','laptops Kenya','TVs Kenya','earphones Kenya','generators Kenya') THEN 'Electronics'
            WHEN keyword IN ('clothes online Kenya','sneakers Kenya','handbags Kenya','segunda Kenya','mitumba Kenya') THEN 'Fashion'
            WHEN keyword IN ('supermarket Kenya','food delivery Kenya','cooking gas Kenya','unga Kenya','sukuma wiki Kenya') THEN 'Food & Grocery'
            WHEN keyword IN ('salon equipment Kenya','wigs Kenya','weaves Kenya','skincare Kenya','perfume Kenya') THEN 'Beauty & Salon'
            WHEN keyword IN ('houses for sale Nairobi','land Kenya','bedsitter Nairobi','Airbnb Kenya','rental houses Kenya') THEN 'Real Estate'
            WHEN keyword IN ('fertilizer Kenya','seeds Kenya','poultry Kenya','greenhouse Kenya','dairy farming Kenya') THEN 'Agriculture'
            WHEN keyword IN ('loans Kenya','Mpesa Kenya','Fuliza Kenya','forex Kenya','crypto Kenya') THEN 'Finance'
            WHEN keyword IN ('pharmacy Kenya','hospital Kenya','insurance Kenya','chemist Kenya','dawa Kenya') THEN 'Health'
        END AS category,
        ROUND(AVG(interest), 1) AS avg_interest
    FROM search_trends
    WHERE interest > 0
    GROUP BY category
    ORDER BY avg_interest DESC;
"""
df2 = pd.read_sql(q2, engine)
colors = ["#2E86AB","#A23B72","#F18F01","#C73E1D","#3B1F2B","#44BBA4","#E94F37","#393E41"]

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.bar(df2["category"], df2["avg_interest"], color=colors, edgecolor="white", width=0.6)
ax.set_ylabel("Average Search Interest (0-100)", fontsize=11)
ax.set_title("🇰🇪 Kenya Consumer Demand by Category\n(Jun 2025 — Jun 2026)",
             fontsize=13, fontweight="bold", pad=15)
ax.set_ylim(0, 70)
ax.grid(axis="y", linestyle="--", alpha=0.4)
plt.xticks(rotation=30, ha="right", fontsize=10)
for bar, val in zip(bars, df2["avg_interest"]):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8,
            str(val), ha="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/demand_by_category.png", dpi=150)
plt.show()
print("✅ Chart 2 saved — Demand by Category")

# ─────────────────────────────────────────
# CHART 3: Monthly Demand Trend
# ─────────────────────────────────────────
q3 = """
    SELECT
        TO_CHAR(date, 'Mon YY')       AS month,
        DATE_TRUNC('month', date)     AS month_date,
        ROUND(AVG(interest), 1)       AS avg_interest
    FROM search_trends
    WHERE interest > 0
    GROUP BY TO_CHAR(date, 'Mon YY'), DATE_TRUNC('month', date)
    ORDER BY month_date ASC;
"""
df3 = pd.read_sql(q3, engine)

fig, ax = plt.subplots(figsize=(13, 5))
ax.plot(df3["month"], df3["avg_interest"],
        marker="o", color="#F18F01", linewidth=2.5, markersize=7)
ax.fill_between(range(len(df3)), df3["avg_interest"], alpha=0.15, color="#F18F01")
ax.set_ylabel("Average Search Interest", fontsize=11)
ax.set_title("🇰🇪 Kenya Monthly Consumer Demand Trend\n(Jun 2025 — Jun 2026)",
             fontsize=13, fontweight="bold", pad=15)
ax.set_xticks(range(len(df3)))
ax.set_xticklabels(df3["month"], rotation=45, ha="right", fontsize=9)
ax.set_ylim(0, 70)
ax.grid(axis="y", linestyle="--", alpha=0.4)
for i, val in enumerate(df3["avg_interest"]):
    ax.text(i, val + 1, str(val), ha="center", fontsize=8, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/monthly_trend.png", dpi=150)
plt.show()
print("✅ Chart 3 saved — Monthly Trend")

# ─────────────────────────────────────────
# CHART 4: Rising vs Falling Products
# ─────────────────────────────────────────
q4 = """
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
df4 = pd.read_sql(q4, engine)
df4["keyword"] = df4["keyword"].str.replace(" Kenya", "").str.replace(" Nairobi", "")
df4["change"]  = df4["recent_avg"] - df4["previous_avg"]
colors_change  = ["#44BBA4" if x >= 0 else "#C73E1D" for x in df4["change"]]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(df4["keyword"], df4["change"], color=colors_change, edgecolor="white")
ax.axvline(0, color="black", linewidth=0.8)
ax.set_xlabel("Change in Search Interest (Recent 3M vs Previous 3M)", fontsize=11)
ax.set_title("🇰🇪 Rising vs Falling Products in Kenya",
             fontsize=13, fontweight="bold", pad=15)
ax.invert_yaxis()
ax.grid(axis="x", linestyle="--", alpha=0.4)
for bar, val in zip(bars, df4["change"]):
    ax.text(bar.get_width() + (0.3 if val >= 0 else -0.3),
            bar.get_y() + bar.get_height() / 2,
            f"{val:+.1f}", va="center", fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/rising_vs_falling.png", dpi=150)
plt.show()
print("✅ Chart 4 saved — Rising vs Falling")

engine.dispose()
print("\n🎉 All 4 charts saved to outputs/ folder!")
print("📁 Location: kenya_demand_analysis/outputs/")