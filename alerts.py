import requests
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from config import DB_CONFIG, TELEGRAM_CONFIG

engine = create_engine(
    f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
)

# ─────────────────────────────────────────
# Telegram Sender Function
# ─────────────────────────────────────────
def send_telegram(message):
    """Send a message via Telegram Bot."""
    url = f"https://api.telegram.org/bot{TELEGRAM_CONFIG['bot_token']}/sendMessage"
    payload = {
        "chat_id"    : TELEGRAM_CONFIG["chat_id"],
        "text"       : message,
        "parse_mode" : "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("OK Telegram alert sent!")
        else:
            print(f"ERR Telegram failed: {response.text}")
    except Exception as e:
        print(f"ERR Telegram error: {e}")

# ─────────────────────────────────────────
# ALERT 1: Demand Spike Alert
# Keywords that hit above 80 this week
# ─────────────────────────────────────────
print("Checking for demand spikes...")

q_spikes = """
    SELECT
        keyword,
        MAX(interest)  AS peak_interest,
        ROUND(AVG(interest), 1) AS avg_interest,
        MAX(date)      AS latest_date
    FROM search_trends
    WHERE
        date >= CURRENT_DATE - INTERVAL '7 days'
        AND interest >= 80
    GROUP BY keyword
    ORDER BY peak_interest DESC;
"""

conn = engine.connect()
df_spikes = pd.read_sql(q_spikes, conn)

if not df_spikes.empty:
    print(f"Found {len(df_spikes)} spike(s)!")

    message = (
        f"*Kenya Demand Analysis*\n"
        f"*DEMAND SPIKE ALERT*\n"
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    )

    for _, row in df_spikes.iterrows():
        message += (
            f"Keyword:  {row['keyword']}\n"
            f"Peak:     {row['peak_interest']}/100\n"
            f"Average:  {row['avg_interest']}/100\n"
            f"Date:     {row['latest_date']}\n\n"
        )

    send_telegram(message)
else:
    print("No spikes found this week.")

# ─────────────────────────────────────────
# ALERT 2: Weekly Summary Report
# Sent every Monday with top 5 insights
# ─────────────────────────────────────────
print("Sending weekly summary...")

q_summary = """
    SELECT
        keyword,
        ROUND(AVG(interest), 1) AS avg_interest
    FROM search_trends
    WHERE
        date >= CURRENT_DATE - INTERVAL '7 days'
        AND interest > 0
    GROUP BY keyword
    ORDER BY avg_interest DESC
    LIMIT 5;
"""

df_summary = pd.read_sql(q_summary, conn)

# ─────────────────────────────────────────
# ALERT 3: Competitor Market Leader
# ─────────────────────────────────────────
q_leaders = """
    SELECT DISTINCT ON (category)
        category,
        brand AS market_leader,
        ROUND(AVG(interest)
            OVER (PARTITION BY category, brand), 1) AS avg_interest
    FROM competitor_trends
    WHERE interest > 0
    ORDER BY category, avg_interest DESC;
"""

df_leaders = pd.read_sql(q_leaders, conn)
conn.close()

# Build weekly summary message
summary_msg = (
    f"*Kenya Demand Analysis*\n"
    f"*WEEKLY MARKET SUMMARY*\n"
    f"Week of: {datetime.now().strftime('%Y-%m-%d')}\n\n"
    f"*TOP 5 PRODUCTS THIS WEEK:*\n"
)

for _, row in df_summary.iterrows():
    bar = "█" * int(row["avg_interest"] / 10)
    summary_msg += f"{row['keyword']}: {row['avg_interest']} {bar}\n"

summary_msg += f"\n*MARKET LEADERS:*\n"
for _, row in df_leaders.iterrows():
    summary_msg += f"{row['category']}: {row['market_leader']} ({row['avg_interest']})\n"

summary_msg += f"\nPowered by Kenya Demand Analysis Pipeline"

send_telegram(summary_msg)
engine.dispose()
print("Alerts complete!")