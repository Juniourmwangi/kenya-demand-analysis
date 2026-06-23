import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from sqlalchemy import create_engine
from config import DB_CONFIG

engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

print("Building Competitor Charts...")

# ── Chart 1: Market Leaders per Category ────────────────
q1 = """
    SELECT DISTINCT ON (category)
        category,
        brand AS market_leader,
        ROUND(AVG(interest) OVER (PARTITION BY category, brand), 1) AS avg_interest
    FROM competitor_trends
    WHERE interest > 0
    ORDER BY category, avg_interest DESC;
"""
df1 = pd.read_sql(q1, engine)
colors = ["#2E86AB","#A23B72","#F18F01","#C73E1D","#44BBA4"]

fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(df1["category"], df1["avg_interest"], color=colors, edgecolor="white")
ax.set_xlabel("Average Search Interest (0-100)", fontsize=11)
ax.set_title("Kenya Market Leaders by Category\n(Jun 2025 - Jun 2026)",
             fontsize=13, fontweight="bold", pad=15)
ax.set_xlim(0, 110)
ax.invert_yaxis()
ax.grid(axis="x", linestyle="--", alpha=0.4)
for bar, (_, row) in zip(bars, df1.iterrows()):
    ax.text(bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            f"{row['market_leader']}  ({row['avg_interest']})",
            va="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/competitor_market_leaders.png", dpi=150)
plt.show()
print("OK Chart 1 saved — Market Leaders")

# ── Chart 2: E-Commerce Battle ───────────────────────────
q2 = """
    SELECT brand, ROUND(AVG(interest), 1) AS avg_interest
    FROM competitor_trends
    WHERE category = 'E-Commerce' AND interest > 0
    GROUP BY brand
    ORDER BY avg_interest DESC;
"""
df2 = pd.read_sql(q2, engine)
colors2 = ["#2E86AB","#F18F01","#44BBA4","#C73E1D","#A23B72"]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(df2["brand"], df2["avg_interest"], color=colors2, edgecolor="white")
ax.set_ylabel("Average Search Interest", fontsize=11)
ax.set_title("Kenya E-Commerce Battle\nJumia vs Kilimall vs Jiji vs Others",
             fontsize=13, fontweight="bold", pad=15)
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle="--", alpha=0.4)
for bar, val in zip(bars, df2["avg_interest"]):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(val), ha="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/competitor_ecommerce.png", dpi=150)
plt.show()
print("OK Chart 2 saved — E-Commerce Battle")

# ── Chart 3: Banking Battle ──────────────────────────────
q3 = """
    SELECT brand, ROUND(AVG(interest), 1) AS avg_interest
    FROM competitor_trends
    WHERE category = 'Banking' AND interest > 0
    GROUP BY brand
    ORDER BY avg_interest DESC;
"""
df3 = pd.read_sql(q3, engine)
colors3 = ["#C73E1D","#2E86AB","#F18F01","#44BBA4","#A23B72"]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(df3["brand"], df3["avg_interest"], color=colors3, edgecolor="white")
ax.set_ylabel("Average Search Interest", fontsize=11)
ax.set_title("Kenya Banking Battle\nAbsa vs KCB vs Equity vs Others",
             fontsize=13, fontweight="bold", pad=15)
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle="--", alpha=0.4)
for bar, val in zip(bars, df3["avg_interest"]):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(val), ha="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/competitor_banking.png", dpi=150)
plt.show()
print("OK Chart 3 saved — Banking Battle")

# ── Chart 4: Betting Battle ──────────────────────────────
q4 = """
    SELECT brand, ROUND(AVG(interest), 1) AS avg_interest
    FROM competitor_trends
    WHERE category = 'Betting' AND interest > 0
    GROUP BY brand
    ORDER BY avg_interest DESC;
"""
df4 = pd.read_sql(q4, engine)
colors4 = ["#44BBA4","#2E86AB","#F18F01","#C73E1D","#A23B72"]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(df4["brand"], df4["avg_interest"], color=colors4, edgecolor="white")
ax.set_ylabel("Average Search Interest", fontsize=11)
ax.set_title("Kenya Betting Battle\nBetika vs Sportpesa vs Others",
             fontsize=13, fontweight="bold", pad=15)
ax.set_ylim(0, 100)
ax.grid(axis="y", linestyle="--", alpha=0.4)
for bar, val in zip(bars, df4["avg_interest"]):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            str(val), ha="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/competitor_betting.png", dpi=150)
plt.show()
print("OK Chart 4 saved — Betting Battle")

# ── Chart 5: Top 10 Overall Brands ──────────────────────
q5 = """
    SELECT brand, category,
           ROUND(AVG(interest), 1) AS avg_interest
    FROM competitor_trends
    WHERE interest > 0
    GROUP BY brand, category
    ORDER BY avg_interest DESC
    LIMIT 10;
"""
df5 = pd.read_sql(q5, engine)
cat_colors = {
    "Telecom"      : "#2E86AB",
    "Betting"      : "#44BBA4",
    "E-Commerce"   : "#F18F01",
    "Banking"      : "#C73E1D",
    "Food Delivery": "#A23B72"
}
bar_colors = [cat_colors[c] for c in df5["category"]]
legend_patches = [mpatches.Patch(color=v, label=k)
                  for k, v in cat_colors.items()]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(df5["brand"], df5["avg_interest"],
               color=bar_colors, edgecolor="white")
ax.set_xlabel("Average Search Interest (0-100)", fontsize=11)
ax.set_title("Top 10 Most Searched Brands in Kenya\n(Jun 2025 - Jun 2026)",
             fontsize=13, fontweight="bold", pad=15)
ax.invert_yaxis()
ax.set_xlim(0, 110)
ax.grid(axis="x", linestyle="--", alpha=0.4)
ax.legend(handles=legend_patches, loc="lower right", fontsize=9)
for bar, val in zip(bars, df5["avg_interest"]):
    ax.text(bar.get_width() + 1,
            bar.get_y() + bar.get_height() / 2,
            str(val), va="center", fontsize=9, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/competitor_top10_brands.png", dpi=150)
plt.show()
print("OK Chart 5 saved — Top 10 Brands")

engine.dispose()
print("\nAll competitor charts saved to outputs/ folder!")