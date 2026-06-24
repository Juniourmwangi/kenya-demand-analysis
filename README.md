# 🇰🇪 Kenya Consumer Demand Analysis

> A complete professional market intelligence system tracking real-time consumer demand, competitor brands, and city-level insights across the Kenyan market — built with Python, PostgreSQL, Power BI, and Telegram automation.

---

##  Project Status: COMPLETE

| Feature | Status |
|---------|--------|
| Automated Weekly Refresh | ✅ Complete |
| Competitor Brand Tracking | ✅ Complete |
| Telegram Demand Alerts | ✅ Complete |
| City-Level Breakdown | ✅ Complete |
| Power BI Dashboard | ✅ Complete |

---

## Project Overview

This project answers one powerful question:

> **"What are Kenyans actively searching for online — and what does that tell us about market demand?"**

Using Google Trends data, this pipeline tracks **40 keywords across 8 industries**, **25 brands across 5 categories**, and **5 major Kenyan cities** — storing everything in a PostgreSQL database, analysing with SQL, visualizing with Python and Power BI, and delivering weekly alerts via Telegram.

---

##  Key Findings

### Top 10 Most Searched Products in Kenya

| Rank | Product | Avg Interest |
|------|---------|-------------|
| 1 | Land Kenya | 77.7 |
| 2 | Mpesa Kenya | 72.2 |
| 3 | Seeds Kenya | 70.8 |
| 4 | Insurance Kenya | 69.7 |
| 5 | Perfume Kenya | 65.3 |
| 6 | Laptops Kenya | 64.8 |
| 7 | Supermarket Kenya | 61.6 |
| 8 | TVs Kenya | 60.9 |
| 9 | Sneakers Kenya | 60.1 |
| 10 | Hospital Kenya | 48.4 |

### Market Leaders by Category

| Category | Market Leader | Avg Interest |
|----------|--------------|-------------|
| Telecom | Safaricom | 87.7 |
| Betting | Betika | 75.5 |
| E-Commerce | Jumia Kenya | 71.7 |
| Banking | Absa Kenya | 68.3 |
| Food Delivery | Glovo Kenya | 52.9 |

### City Demand Rankings

| Rank | City | Avg Interest |
|------|------|-------------|
| 1 | Nairobi | 19.7 |
| 2 | Nakuru | 5.0 |
| 3 | Eldoret | 2.5 |
| 4 | Mombasa | 1.0 |
| 5 | Kisumu | 1.0 |

### Key Insights
-  **Land** is the #1 most searched product — Kenyans are actively looking to buy
-  **Mpesa** at #2 shows how deeply fintech is embedded in daily life
-  **Agriculture** has massive demand but few businesses serving it online
-  **Electronics** is the top performing category overall
-  **November & December** are Kenya's peak consumer demand months
-  **TVs** is the only product showing consistent demand growth
-  **Betika** is crushing Sportpesa (75.5 vs 28.8) — major market shift
-  **Absa** surprisingly leads Banking over Equity and KCB
-  **Eldoret** leads Agriculture searches — Rift Valley farming belt effect

---

##  Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.13 | Core programming language |
| pytrends | Google Trends API connector |
| pandas | Data cleaning & transformation |
| PostgreSQL 18 | Professional database storage |
| pgAdmin 4 | Database visual interface |
| SQLAlchemy | Python-PostgreSQL bridge |
| psycopg2 | Database driver |
| matplotlib | Data visualization & charts |
| openpyxl | Excel report generation |
| requests | Telegram Bot API |
| Power BI Desktop | Interactive dashboard |
| Task Scheduler | Automated weekly runs |
| Git & GitHub | Version control & portfolio |
| VS Code | Development environment |

---

##  Project Structure

```
kenya_demand_analysis/
│
├── config.py                 # Database & Telegram credentials (not uploaded)
├── test_connection.py        # PostgreSQL connection test
├── pull_data.py              # Google Trends data pipeline (40 keywords)
├── queries.py                # SQL analysis queries
├── visualize.py              # Python chart generation
├── export_excel.py           # Styled Excel report export
├── competitor_tracking.py    # Competitor brand data pipeline
├── competitor_charts.py      # Competitor visualization
├── county_breakdown.py       # City-level demand analysis
├── county_charts.py          # City comparison charts
├── alerts.py                 # Telegram demand spike alerts
├── scheduler.py              # Automated weekly pipeline runner
├── list_databases.py         # Database verification utility
│
├── logs/
│   └── scheduler.log         # Auto-generated run history
│
└── outputs/
    ├── Kenya_Demand_Analysis.xlsx        # 5-sheet styled Excel report
    ├── Kenya_Demand_Analysis.pbix        # Power BI dashboard
    ├── top10_products.png                # Top 10 products chart
    ├── demand_by_category.png            # Category comparison chart
    ├── monthly_trend.png                 # 12-month trend line
    ├── rising_vs_falling.png             # Growth analysis chart
    ├── competitor_market_leaders.png     # Market leaders chart
    ├── competitor_ecommerce.png          # E-commerce battle
    ├── competitor_banking.png            # Banking battle
    ├── competitor_betting.png            # Betting battle
    ├── competitor_top10_brands.png       # Top 10 brands
    ├── city_demand_comparison.png        # City comparison
    ├── city_category_heatmap.png         # City vs category heatmap
    └── city_category_comparison.png      # City category breakdown
```

---

##  Database Schema

### Table 1: search_trends
```sql
CREATE TABLE search_trends (
    id          SERIAL PRIMARY KEY,
    date        DATE NOT NULL,
    keyword     VARCHAR(100) NOT NULL,
    interest    INTEGER,
    region      VARCHAR(50) DEFAULT 'Kenya',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**2,120 rows** | 40 keywords | 8 categories | 12 months

### Table 2: competitor_trends
```sql
CREATE TABLE competitor_trends (
    id          SERIAL PRIMARY KEY,
    date        DATE NOT NULL,
    brand       VARCHAR(100) NOT NULL,
    category    VARCHAR(50) NOT NULL,
    interest    INTEGER,
    region      VARCHAR(50) DEFAULT 'Kenya',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**1,325 rows** | 25 brands | 5 categories

### Table 3: county_trends
```sql
CREATE TABLE county_trends (
    id          SERIAL PRIMARY KEY,
    county      VARCHAR(100) NOT NULL,
    keyword     VARCHAR(100) NOT NULL,
    interest    INTEGER,
    category    VARCHAR(50),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
**5 cities** | Nairobi, Mombasa, Kisumu, Nakuru, Eldoret

---

##  How to Run

### 1. Clone the repository
```bash
git clone https://github.com/Juniourmwangi/kenya-demand-analysis.git
cd kenya-demand-analysis
```

### 2. Install dependencies
```bash
pip install pytrends pandas psycopg2-binary sqlalchemy matplotlib openpyxl requests
```

### 3. Set up PostgreSQL 18
- Install PostgreSQL 18 + pgAdmin 4
- Create database: `kenya_demand_analysis`
- Run the 3 table creation SQL scripts above

### 4. Configure credentials
Create `config.py`:
```python
DB_CONFIG = {
    "host"     : "localhost",
    "database" : "kenya_demand_analysis",
    "user"     : "postgres",
    "password" : "your_password",
    "port"     : "5432"
}

TELEGRAM_CONFIG = {
    "bot_token" : "your_telegram_bot_token",
    "chat_id"   : "your_chat_id"
}
```

### 5. Run the full pipeline
```bash
# Test connection
py test_connection.py

# Pull Google Trends data (40 keywords)
py pull_data.py

# Run SQL analysis
py queries.py

# Generate Python charts
py visualize.py

# Export Excel report
py export_excel.py

# Pull competitor data (25 brands)
py competitor_tracking.py
py competitor_charts.py

# Pull city-level data
py county_breakdown.py
py county_charts.py

# Send Telegram alerts
py alerts.py

# Or run everything automatically
py scheduler.py
```

---

##  Automation

The project runs **automatically every Monday at 8:00 AM** via Windows Task Scheduler:

```
scheduler.py → pull_data.py → queries.py → visualize.py → export_excel.py → alerts.py
```

Every run is logged to `logs/scheduler.log` with timestamps and success/error status.

---

##  Telegram Alerts

The system sends two types of automatic Telegram messages:

1. **Demand Spike Alert** — when any keyword exceeds 80/100 interest score
2. **Weekly Market Summary** — top 5 products + market leaders every Monday

---

##  Power BI Dashboard

Three interactive pages connected to PostgreSQL:

| Page | Content |
|------|---------|
| Kenya Market Overview | Top 10 products, category donut, monthly trend, KPI cards |
| Competitor Battle | Brand rankings, category slicer, brand trend over time |
| City Demand | City comparison bar, demand matrix by city and category |

---

## Charts Generated (13 Total)

| Chart | File |
|-------|------|
| Top 10 Products | top10_products.png |
| Demand by Category | demand_by_category.png |
| Monthly Trend | monthly_trend.png |
| Rising vs Falling | rising_vs_falling.png |
| Market Leaders | competitor_market_leaders.png |
| E-Commerce Battle | competitor_ecommerce.png |
| Banking Battle | competitor_banking.png |
| Betting Battle | competitor_betting.png |
| Top 10 Brands | competitor_top10_brands.png |
| City Comparison | city_demand_comparison.png |
| City Heatmap | city_category_heatmap.png |
| City Category Comparison | city_category_comparison.png |

---

##  Future Improvements

- [ ] Power BI Service (cloud publishing for live sharing)
- [ ] Additional counties when Google Trends data improves
- [ ] WhatsApp alerts integration
- [ ] Sentiment analysis on social media mentions
- [ ] Historical data archive (year on year comparison)
- [ ] API endpoint to serve data to web applications

---

## 👨‍💻 Author

**James Mwangi**
- Data Analyst | Web Developer | Internal Auditor 
- X: [@I_am_Mwangi](https://twitter.com/I_am_Mwangi)
- GitHub: [github.com/Juniourmwangi](https://github.com/Juniourmwangi)

---

## 📄 License

MIT License — free to use, modify, and share with attribution.

---

*Built from scratch as a learning project — from zero to a complete professional market intelligence system.*
