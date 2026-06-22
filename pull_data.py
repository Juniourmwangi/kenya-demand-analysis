import time
import pandas as pd
import psycopg2
from pytrends.request import TrendReq
from config import DB_CONFIG

# ─────────────────────────────────────────
# Kenya Product Categories & Keywords
# ─────────────────────────────────────────

# Google Trends allows max 5 keywords per request
# We split into groups and pull each separately

keyword_groups = [
    # Electronics
    ["smartphones Kenya", "laptops Kenya", "TVs Kenya", "earphones Kenya", "generators Kenya"],
    # Fashion
    ["clothes online Kenya", "sneakers Kenya", "handbags Kenya", "segunda Kenya", "mitumba Kenya"],
    # Food & Grocery
    ["supermarket Kenya", "food delivery Kenya", "cooking gas Kenya", "unga Kenya", "sukuma wiki Kenya"],
    # Beauty & Salon
    ["salon equipment Kenya", "wigs Kenya", "weaves Kenya", "skincare Kenya", "perfume Kenya"],
    # Real Estate
    ["houses for sale Nairobi", "land Kenya", "bedsitter Nairobi", "Airbnb Kenya", "rental houses Kenya"],
    # Agriculture
    ["fertilizer Kenya", "seeds Kenya", "poultry Kenya", "greenhouse Kenya", "dairy farming Kenya"],
    # Finance
    ["loans Kenya", "Mpesa Kenya", "Fuliza Kenya", "forex Kenya", "crypto Kenya"],
    # Health
    ["pharmacy Kenya", "hospital Kenya", "insurance Kenya", "chemist Kenya", "dawa Kenya"],
]

# ─────────────────────────────────────────
# STEP 1: Pull All Groups from Google Trends
# ─────────────────────────────────────────
print("🔍 Connecting to Google Trends...")

pytrends = TrendReq(hl='en-KE', tz=180)

all_data = []  # Store all results here

for i, keywords in enumerate(keyword_groups):
    print(f"   Pulling group {i+1}/{len(keyword_groups)}: {keywords}")

    try:
        pytrends.build_payload(
            kw_list  = keywords,
            geo      = "KE",
            timeframe= "today 12-m"
        )

        df = pytrends.interest_over_time()

        if df.empty:
            print(f"   ⚠️  No data for group {i+1}, skipping...")
            continue

        df.drop(columns=["isPartial"], inplace=True)
        df.reset_index(inplace=True)
        all_data.append(df)

        # Pause between requests - avoid Google blocking us
        time.sleep(3)

    except Exception as e:
        print(f"   ❌ Error on group {i+1}: {e}")
        time.sleep(10)
        continue

print(f"\n✅ Pulled {len(all_data)} groups successfully!")

# ─────────────────────────────────────────
# STEP 2: Clean & Reshape All Data
# ─────────────────────────────────────────
print("\n🧹 Cleaning data...")

cleaned_frames = []

for df in all_data:
    df_melted = df.melt(
        id_vars   = "date",
        var_name  = "keyword",
        value_name= "interest"
    )
    cleaned_frames.append(df_melted)

# Combine all groups into one big table
df_final = pd.concat(cleaned_frames, ignore_index=True)
df_final["region"] = "Kenya"
df_final["date"]   = pd.to_datetime(df_final["date"]).dt.date

print(f"✅ Total rows ready: {len(df_final)}")
print(df_final.head(10))

# ─────────────────────────────────────────
# STEP 3: Save to PostgreSQL
# ─────────────────────────────────────────
print("\n💾 Saving to PostgreSQL...")

conn   = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Clear old data first
cursor.execute("TRUNCATE TABLE search_trends;")

for _, row in df_final.iterrows():
    cursor.execute("""
        INSERT INTO search_trends (date, keyword, interest, region)
        VALUES (%s, %s, %s, %s)
    """, (row["date"], row["keyword"], row["interest"], row["region"]))

conn.commit()
cursor.close()
conn.close()

print(f"✅ {len(df_final)} rows saved to PostgreSQL!")
print("🎉 Full Kenya Market Pipeline Complete!")