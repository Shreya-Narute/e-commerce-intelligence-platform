# Power BI Setup Guide

This guide explains how to connect **Power BI Desktop** to the E-Commerce
Intelligence & Decision Support Platform PostgreSQL database, import the
analytical SQL views from [`powerbi_views.sql`](./powerbi_views.sql), and build
the recommended dashboard pages.

> **No `.pbix` file is committed to the repository.** Build the dashboard in
> Power BI Desktop using the SQL views and instructions below.

---

## 1. Prerequisites

1. **Power BI Desktop** (Windows) - install from
   https://powerbi.microsoft.com/desktop/.
2. A **PostgreSQL driver** so Power BI can talk to PostgreSQL 16:
   - **Recommended:** the official *PostgreSQL ODBC Driver* (psqlODBC) from
     https://www.postgresql.org/ftp/odbc/versions/msi/, **or**
   - the **Npgsql** .NET provider (used by the native Power BI PostgreSQL
     connector). The Power BI Desktop PostgreSQL connector ships with Npgsql
     bundled, so in most cases no separate driver install is required.
3. A running database populated with the Olist dataset (see the main README
   "Data Ingestion" section). The Dockerized database exposes PostgreSQL on host
   port **5433**.

---

## 2. Create the SQL views in PostgreSQL

Before opening Power BI, create the five analytical views in the database. From
the project root, run the SQL file against the database:

```bash
# Using the psql client (replace <password> with your POSTGRES_PASSWORD):
psql -h localhost -p 5433 -U postgres -d ecommerce_intelligence -f docs/powerbi_views.sql
```

Alternatively, open `docs/powerbi_views.sql` in **pgAdmin** (or DBeaver),
connect to the `ecommerce_intelligence` database, and execute the whole script.

All statements use `CREATE OR REPLACE VIEW`, so the script is safe to re-run.

### Views created

| View | Grain | Key measures |
|---|---|---|
| `vw_sales_monthly` | Year-month (delivered orders) | revenue, order_count, avg_order_value |
| `vw_product_performance` | Product | total_revenue, order_count, avg_price, category |
| `vw_customer_rfm` | customer_unique_id | recency_days, frequency, monetary, R/F/M scores, segment |
| `vw_seller_performance` | Seller (state) | total_revenue, order_count, avg_review_score |
| `vw_delivery_performance` | Delivered order | delivery_days, on_time, review_score, customer_state |

> **Empty until data is ingested.** These views return **zero rows** until the
> Olist CSV files have been loaded with `python scripts/ingest_data.py`. An empty
> result set is normal and is **not** a connection error. Do not invent sample
> rows to make a dashboard look populated.

---

## 3. Connect Power BI Desktop to PostgreSQL

1. Open Power BI Desktop and click **Get Data** > **Database** > **PostgreSQL database**.
2. Enter the connection details for the Dockerized database:

   | Field | Value |
   |---|---|
   | Server | `localhost` |
   | Port | `5433` |
   | Database | `ecommerce_intelligence` |
   | Username | `postgres` |
   | Password | *(the value of `POSTGRES_PASSWORD` from your local `.env` - never commit this)* |

3. Click **OK**. If prompted, install/accept the PostgreSQL driver.
4. In the navigator pane, expand the database and select the five views:
   `vw_sales_monthly`, `vw_product_performance`, `vw_customer_rfm`,
   `vw_seller_performance`, `vw_delivery_performance`.
5. Click **Load** (or **Transform Data** to review in Power Query first).

### Connecting to a local (non-Docker) database

If you run PostgreSQL directly on the host instead of through Docker, use the
local connection details from `backend/.env` (typically port `5432`).

---

## 4. Recommended dashboard pages

Build five report pages, one per theme:

### Page 1 - Executive Overview (source: `vw_sales_monthly`)
- KPI cards: **Total Revenue**, **Total Orders**, **Average Order Value**.
- Line chart: revenue over `year_month`.
- Column chart: order count over `year_month`.

### Page 2 - Sales Performance (source: `vw_sales_monthly` + others)
- Monthly trend line of revenue and AOV (`vw_sales_monthly`).
- Revenue by customer state (use `vw_delivery_performance.customer_state`
  joined to its revenue, or build a small state-revenue measure).
- Revenue by product category (source: `vw_product_performance`, grouped by
  `category`).

### Page 3 - Product & Seller Performance
- Top-N products by `total_revenue` (`vw_product_performance`).
- Seller leaderboard by `total_revenue` and `avg_review_score`
  (`vw_seller_performance`).
- Map / bar chart of seller revenue by `seller_state`.

### Page 4 - Customer & RFM Segmentation (source: `vw_customer_rfm`)
- Donut/pie of customer count by `segment`.
- Scatter plot: `recency_days` (x) vs `monetary` (y), sized by `frequency`,
  coloured by `segment`.
- KPI cards: total customers, average monetary, average recency.

### Page 5 - Delivery, Satisfaction & Forecasting (source: `vw_delivery_performance`)
- KPI: **On-Time Delivery %** (share of rows where `on_time = true`).
- Histogram of `delivery_days`.
- Bar chart of average `review_score` by `customer_state`.
- Forecasting note: the Simple-Exponential-Smoothing forecasts are
  produced by the FastAPI `/api/v1/forecasting` endpoint and the
  `/api/v1/model-eval` metrics - those are **not** SQL views. Export the
  forecast JSON to a CSV and load it as an extra Power BI table if you want the
  forecast line on this page.

---

## 5. Example DAX measures

Create these measures under the relevant tables in Power BI Desktop:

```dax
-- Total Revenue (works on any view that exposes a revenue column,
-- e.g. vw_sales_monthly.revenue or vw_product_performance.total_revenue)
Total Revenue = SUM('vw_sales_monthly'[revenue])

-- Average Order Value = revenue / distinct order count
AOV =
DIVIDE(
    SUM('vw_sales_monthly'[revenue]),
    SUM('vw_sales_monthly'[order_count]),
    0
)

-- On-Time Delivery % (vw_delivery_performance)
On-Time Delivery % =
DIVIDE(
    CALCULATE(COUNTROWS('vw_delivery_performance'),
              'vw_delivery_performance'[on_time] = TRUE()),
    COUNTROWS('vw_delivery_performance'),
    0
)

-- Average Review Score (vw_seller_performance or vw_delivery_performance)
Avg Review Score = AVERAGE('vw_seller_performance'[avg_review_score])
```

---

## 6. Refreshing data

- After re-ingesting or updating the Olist data, click **Refresh** in Power BI
  Desktop. The views re-evaluate against the live database on every refresh.
- Because the views are server-side, no transformation logic lives in the
  `.pbix` file - keeping the dataset and the REST API consistent.

---

## 7. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Connection refused on 5433 | The Docker database container is not running. Start it with `docker compose up -d db` (do not delete the volume). |
| All visuals show "No data" | The Olist CSVs have not been ingested yet. Run `python scripts/ingest_data.py` and refresh. |
| Authentication failed | Use the `POSTGRES_PASSWORD` from your local `.env`; the default is `postgres`. |
| `vw_customer_rfm` scores differ from the API | Expected - see the note in `powerbi_views.sql`. The Python `app.analytics.rfm` implementation (pandas `qcut`) is authoritative. |

---

## 8. Repository note

No `.pbix` file is committed to this repository. Anyone reproducing the
dashboard should follow this guide. Keep any `.pbix` you create out of version
control (it may contain embedded credentials), and **never commit `.env`
files, `data/raw/*.csv`, or database credentials to Git**.
