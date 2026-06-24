import pandas as pd
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
from config import DB_CONFIG

engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

print("Building City Comparison Charts...")

# ── Chart 1: Overall City Demand ─────────────────────────
q1 = """
    SELECT
        county AS city,
        ROUND(AVG(interest), 1) AS avg_interest
    FROM county_trends
    WHERE interest > 0
    GROUP BY county
    ORDER BY avg_interest DESC;
"""
df1 = pd.read_sql(q1, engine)
colors = ["#2E86AB","#F18F01","#44BBA4","#C73E1D","#A23B72"]

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(df1["city"], df1["avg_interest"],
              color=colors[:len(df1)], edgecolor="white", width=0.5)
ax.set_ylabel("Average Search Interest (0-100)", fontsize=11)
ax.set_title("Kenya City Demand Comparison\nNairobi vs Mombasa vs Kisumu vs Nakuru vs Eldoret",
             fontsize=13, fontweight="bold", pad=15)
ax.set_ylim(0, max(df1["avg_interest"]) + 10)
ax.grid(axis="y", linestyle="--", alpha=0.4)
for bar, val in zip(bars, df1["avg_interest"]):
    ax.text(bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.3,
            str(val), ha="center", fontsize=11, fontweight="bold")
plt.tight_layout()
plt.savefig("outputs/city_demand_comparison.png", dpi=150)
plt.show()
print("OK Chart 1 saved — City Demand Comparison")

# ── Chart 2: City vs Category Heatmap ───────────────────
q2 = """
    SELECT
        county AS city,
        category,
        ROUND(AVG(interest), 1) AS avg_interest
    FROM county_trends
    WHERE interest > 0
    GROUP BY county, category
    ORDER BY city, category;
"""
df2 = pd.read_sql(q2, engine)

if not df2.empty:
    pivot = df2.pivot(
        index="category",
        columns="city",
        values="avg_interest"
    ).fillna(0)

    fig, ax = plt.subplots(figsize=(10, 5))
    im = ax.imshow(pivot.values, cmap="Blues", aspect="auto")

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels(pivot.columns, fontsize=11)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=11)
    ax.set_title("Kenya Demand Heatmap — City vs Category",
                 fontsize=13, fontweight="bold", pad=15)

    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            val = pivot.values[i][j]
            if val > 0:
                ax.text(j, i, str(round(val, 1)),
                        ha="center", va="center",
                        fontsize=10, fontweight="bold",
                        color="white" if val > 30 else "black")

    plt.colorbar(im, ax=ax, label="Search Interest")
    plt.tight_layout()
    plt.savefig("outputs/city_category_heatmap.png", dpi=150)
    plt.show()
    print("OK Chart 2 saved — City Category Heatmap")

# ── Chart 3: Category Comparison per City ───────────────
q3 = """
    SELECT
        category,
        MAX(CASE WHEN county = 'Nairobi'  THEN interest END) AS nairobi,
        MAX(CASE WHEN county = 'Mombasa'  THEN interest END) AS mombasa,
        MAX(CASE WHEN county = 'Kisumu'   THEN interest END) AS kisumu,
        MAX(CASE WHEN county = 'Nakuru'   THEN interest END) AS nakuru,
        MAX(CASE WHEN county = 'Eldoret'  THEN interest END) AS eldoret
    FROM county_trends
    GROUP BY category
    ORDER BY nairobi DESC NULLS LAST;
"""
df3 = pd.read_sql(q3, engine).fillna(0)

x      = range(len(df3))
width  = 0.15
colors = ["#2E86AB","#F18F01","#44BBA4","#C73E1D","#A23B72"]
cities = ["nairobi", "mombasa", "kisumu", "nakuru", "eldoret"]
labels = ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"]

fig, ax = plt.subplots(figsize=(12, 6))
for i, (city, label, color) in enumerate(zip(cities, labels, colors)):
    offset = (i - 2) * width
    ax.bar([p + offset for p in x],
           df3[city], width, label=label,
           color=color, edgecolor="white")

ax.set_ylabel("Search Interest", fontsize=11)
ax.set_title("Kenya Category Demand by City",
             fontsize=13, fontweight="bold", pad=15)
ax.set_xticks(x)
ax.set_xticklabels(df3["category"], rotation=20, ha="right", fontsize=10)
ax.legend(fontsize=10)
ax.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.savefig("outputs/city_category_comparison.png", dpi=150)
plt.show()
print("OK Chart 3 saved — Category Comparison by City")

engine.dispose()
print("\nAll city charts saved to outputs/ folder!")