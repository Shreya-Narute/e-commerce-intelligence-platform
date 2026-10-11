# E-Commerce Intelligence & Decision Support Platform

> Customer Intelligence · Sales Analytics · Product Intelligence · Machine Learning · Forecasting

[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-teal.svg)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-blue.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ed.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)

---

## 1. Project Overview & Objectives

The **E-Commerce Intelligence & Decision Support Platform** is an end-to-end,
full-stack analytical platform built on real e-commerce transaction data (the
Brazilian Olist public dataset). It turns raw order, customer, product, seller,
payment, review and geolocation records into decision-making intelligence
through REST APIs, a React dashboard, and Power BI views.

The platform is built on strict data-engineering principles:

- **True relational integrity** - a complete schema modelling orders, items,
  customers, reviews, sellers, payments, products and geolocation.
- **Zero fabricated metrics** - no hard-coded numbers, fake charts or simulated
  figures. Every calculation reflects actual database tables; analytics
  gracefully report `{"status": "no_data"}` (HTTP 200) when the dataset is empty.
- **Separation of concerns** - a clean split between the FastAPI compute/ORM
  layer and the React + TypeScript UI.
- **Production quality** - Docker Compose orchestration, Alembic migrations,
  JWT authentication with Bcrypt hashing, and a pytest test suite.

**Objectives:** sales & revenue analysis, product/category analysis, customer
behaviour analysis, RFM segmentation with K-Means, delivery & seller
performance, payment analysis, customer engagement-risk analysis, sales
forecasting with model evaluation, business insights, and an interactive
dashboard + Power BI views.

> The app is **not** deployed publicly. It runs locally via Docker Compose.

---

## 2. Architecture & Data Flow

```text
                       ┌─────────────────────────────────────────────┐
   Browser             │  React 18 + TypeScript + Vite               │
   (port 3001)         │  Tailwind CSS · Recharts · React Router     │
                       │  Axios client (JWT interceptors)             │
                       └──────────────────────┬──────────────────────┘
                                              │  /api/v1/* (relative in Docker)
                       ┌──────────────────────▼──────────────────────┐
   Docker network      │  Nginx (frontend container, port 80→3001)   │
                       │  proxies /api/ → backend:8000/api/           │
                       └──────────────────────┬──────────────────────┘
                                              │
                       ┌──────────────────────▼──────────────────────┐
   Backend              │  FastAPI / Uvicorn (port 8000→8001)        │
                       │  15 routers under /api/v1                   │
                       │  Auth (JWT+Bcrypt) · Health · Data Quality  │
                       │  Analytics services · ML (forecasting)      │
                       │  RFM (pandas + scikit-learn K-Means)        │
                       └──────────────────────┬──────────────────────┘
                                              │  SQLAlchemy 2.0
                       ┌──────────────────────▼──────────────────────┐
   Storage             │  PostgreSQL 16 (port 5432→5433)             │
                       │  9 Olist tables + users table               │
                       └──────────────────────▲──────────────────────┘
                                              │  pandas ETL
                       ┌──────────────────────┴──────────────────────┐
   Data                │  data/raw/*.csv (immutable Olist CSVs)      │
                       │  scripts/ingest_data.py                      │
                       └─────────────────────────────────────────────┘
```

Power BI Desktop connects directly to PostgreSQL (port 5433) and reads the
analytical views in `docs/powerbi_views.sql` - see `docs/powerbi_setup.md`.

---

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, React Router, Recharts, Lucide Icons |
| Backend | Python 3.11+, FastAPI, Pydantic v2, Uvicorn, PyJWT, Bcrypt |
| Database & ORM | PostgreSQL 16, SQLAlchemy 2.0, Alembic |
| Data Science | Pandas, NumPy, scikit-learn, SciPy, statsmodels |
| Containerization | Docker, Docker Compose, Nginx |
| Testing | Pytest, pytest-asyncio, HTTPX, Vitest |

---

## 4. Implemented Features (Analytics Modules)

All endpoints are under `/api/v1`. Analytics endpoints require a JWT
(`Authorization: Bearer <token>`). Each returns `{"status": "no_data", ...}`
(HTTP 200) when the database is empty - never a 500.

| # | Module | API base path |
|---|---|---|
| 1 | Sales Intelligence | `/api/v1/sales` |
| 2 | Customer Intelligence | `/api/v1/customers` |
| 3 | RFM Segmentation (quintile + K-Means k=4) | `/api/v1/rfm` |
| 4 | Customer Engagement Risk *(rule-based)* | `/api/v1/engagement` |
| 5 | Product Intelligence | `/api/v1/products` |
| 6 | Seller Intelligence | `/api/v1/sellers` |
| 7 | Delivery & Satisfaction | `/api/v1/delivery` |
| 8 | Payment Intelligence | `/api/v1/payments` |
| 9 | Forecasting (Simple Exponential Smoothing) | `/api/v1/forecasting` |
| 10 | Model Performance | `/api/v1/model-eval` |
| 11 | Business Insights | `/api/v1/insights` |

Supporting routers: Auth `/api/v1/auth`, Health `/api/v1/health`, Data Quality
`/api/v1/data-quality`, Data Explorer `/api/v1/data-explorer`.

### Analytical methodology

- **RFM** (`backend/app/analytics/rfm.py`): per-`customer_unique_id` Recency /
  Frequency / Monetary, scored 1-5 with pandas `qcut` quintiles (Recency
  inverted). Segment labels mirror a rule table (Champions, Loyal Customers, At
  Risk, Lost, New Customers, Potential Loyalists, Others). K-Means (`k=4`,
  `StandardScaler`) clusters the R/F/M features. Returns `insufficient_data`
  for fewer than 10 customers and `no_data` on an empty database.
- **Forecasting** (`backend/app/ml/forecasting.py`): Simple Exponential
  Smoothing (statsmodels) over monthly revenue, evaluated with MAE / RMSE /
  MAPE. Requires 12+ months of data; reports `insufficient_data` otherwise.
- **Engagement risk** (`backend/app/analytics/...`): a **rule-based**
  recency-based risk classification. This is **not** a trained churn-prediction
  model.

---

## 5. Dataset

The platform uses the **Brazilian E-Commerce Public Dataset by Olist** (~100k
real orders, 2016-2018). 9 relational tables:

1. `customers` - customer profiles, state, city, unique ids.
2. `orders` - order lifecycle timestamps (purchase, approved, carrier, customer
   delivery, estimated delivery), status.
3. `order_items` - `product_id`, `seller_id`, unit `price`, `freight_value`.
4. `order_payments` - payment type, installments, payment value.
5. `order_reviews` - review score 1-5, comments.
6. `products` - dimensions and category affiliation.
7. `sellers` - merchant location.
8. `geolocation` - Brazilian ZIP centroids with lat/lng.
9. `product_category_translation` - Portuguese→English category names.

Plus a `users` table for authenticated platform access.

### Data caveats (honest limitations)

- The Olist dataset contains **no reliable product cost or discount fields**.
  The platform therefore does **not** compute or present profit, margin or
  discount impact as real results.
- Customer **engagement risk is rule-based**, not a trained ML churn model.
- **Forecasting needs 12+ months of data**; with less, the API reports
  `insufficient_data`.
- The Power BI views and dashboards are **empty until the Olist CSVs are
  ingested**. No sample rows are fabricated.

### Downloading the dataset

```bash
# Kaggle CLI (recommended):
kaggle datasets download -d olistbr/brazilian-ecommerce -p data/raw --unzip

# Or download the CSVs manually from
# https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
# and place them in data/raw/
```

Place every `olist_*.csv` (and `product_category_name_translation.csv`) into
`data/raw/`.

---

## 6. Project Directory Structure

```text
E-Commerce-Intelligence-Platform/
├── backend/
│   ├── alembic/                # migrations (versions/001_initial_schema.py)
│   ├── app/
│   │   ├── api/v1/             # 15 routers + router.py
│   │   ├── analytics/          # rfm, engagement, etc.
│   │   ├── core/               # config & security settings
│   │   ├── db/                 # engine & session maker
│   │   ├── ml/                 # forecasting
│   │   ├── models/             # SQLAlchemy 2.0 ORM (olist.py, user.py)
│   │   ├── schemas/            # Pydantic v2 models
│   │   ├── services/           # business logic (sales_service, auth_service …)
│   │   └── main.py             # FastAPI entrypoint
│   ├── tests/                 # pytest suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/                    # components, hooks, layouts, pages, services, types
│   ├── package.json · vite.config.ts · tailwind.config.js
│   └── .env.example
├── data/raw/                   # immutable Olist CSVs (not committed)
├── docs/                       # architecture, schema, powerbi_views.sql, powerbi_setup.md
├── docker/                     # backend.Dockerfile, frontend.Dockerfile, nginx.conf
├── scripts/                    # ingest_data.py, download_dataset.py
├── docker-compose.yml
├── .gitignore · README.md · LICENSE
```

---

## 7. Prerequisites

- **Node.js 18+** (for the frontend build)
- **Python 3.11+** (for local backend / scripts)
- **Docker Desktop** (recommended way to run the whole stack)
- **PostgreSQL** client (psql) or pgAdmin (optional, for Power BI view setup)

---

## 8. Environment Setup

Copy the example env files and edit credentials as needed:

```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

`backend/.env` controls the database URL, JWT secret and CORS origins.
`frontend/.env` sets `VITE_API_BASE_URL` (default `http://localhost:8000/api/v1`
for local dev).

> Do not commit `.env` files, `data/raw/*.csv`, or credentials to Git.

---

## 9. Running with Docker Compose (recommended)

From the project root:

```bash
docker compose up --build -d
```

Services and host ports (do not change occupied host ports):

| Service | Container port | Host port | URL |
|---|---|---|---|
| Frontend | 80 | **3001** | http://localhost:3001 |
| Backend  | 8000 | **8001** | http://localhost:8001/docs |
| PostgreSQL | 5432 | **5433** | localhost:5433 |

Start only the database (for local backend dev) without rebuilding the app
images:

```bash
docker compose up -d db
```

---

## 10. Local Development Setup

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
alembic upgrade head            # create schema (fresh DB)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

### Default login

The platform bootstraps an admin account on startup:

- **Email:** `admin@ecommerce-intel.io`
- **Password:** `Admin123!`

---

## 11. Database Migration

Alembic ships a single migration, `001_initial_schema` (`down_revision=None`),
that creates all Olist tables plus the `users` table and seeds the admin.

- **Fresh database:** `alembic upgrade head`
- **Existing database that was created out-of-band:** mark it as migrated
  without running the DDL:
  ```bash
  alembic stamp 001_initial_schema
  ```
  This avoids destructive re-creation while telling Alembic the current revision.

Never run destructive migrations, `TRUNCATE`, or database resets without
explicit approval.

---

## 12. Data Ingestion

With the Olist CSVs in `data/raw/`, load them into PostgreSQL in dependency
order (safe re-runs via `INSERT ... ON CONFLICT DO NOTHING`):

```bash
python scripts/ingest_data.py
```

For a **full reload** (clears the Olist business tables first - destructive,
use with care):

```bash
python scripts/ingest_data.py --truncate
```

Verify integrity with the Data Quality page in the UI or
`GET /api/v1/data-quality`.

---

## 13. URLs

| Purpose | URL |
|---|---|
| Frontend (Docker) | http://localhost:3001 |
| Frontend (Vite dev) | http://localhost:5173 |
| Backend Swagger docs | http://localhost:8001/docs |
| Backend (local uvicorn) | http://localhost:8000 |
| Health | http://localhost:8001/api/v1/health |
| Data Quality | http://localhost:8001/api/v1/data-quality |

---

## 14. Testing

### Backend (pytest)

```bash
cd backend
python -m pytest -v
```

Tests use an in-memory SQLite database with per-function transaction rollback
and seed the admin account. Note: full collection requires the analytics
dependencies (pandas, numpy, scikit-learn, statsmodels). To run the suite inside
Docker (where all dependencies are installed):

```bash
docker compose exec backend python -m pytest -v
```

### Frontend build

```bash
cd frontend
npm run build      # tsc && vite build
```

Component unit tests (Vitest) can be run with `npm run test` when configured.

---

## 15. Power BI

Build dashboards directly against PostgreSQL using the five analytical views.
See [`docs/powerbi_setup.md`](./docs/powerbi_setup.md) for the full step-by-step
guide and [`docs/powerbi_views.sql`](./docs/powerbi_views.sql) for the view
definitions (run that SQL in the database first).

Recommended dashboard pages: Executive Overview, Sales Performance, Product &
Seller Performance, Customer & RFM Segmentation, Delivery/Satisfaction &
Forecasting. No `.pbix` file is committed - build it locally.

---

## 16. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `{"status": "no_data"}` on every analytics endpoint | The Olist CSVs have not been ingested. Run `python scripts/ingest_data.py`. |
| `401 Unauthorized` on analytics endpoints | The JWT is missing/expired. Log in at `/api/v1/auth/login` and send `Authorization: Bearer <token>`. |
| Backend pytest `ModuleNotFoundError: No module named 'numpy'` locally | The local venv is missing analytics packages. Run the suite inside Docker: `docker compose exec backend python -m pytest -v`. |
| RFM returns `insufficient_data` | Fewer than 10 customers are loaded - normal for tiny fixtures. |
| Forecasting returns `insufficient_data` | Fewer than 12 months of data - normal. |
| Cannot connect to PostgreSQL on 5433 | The `db` container is not running. Start it with `docker compose up -d db` (do not delete the volume). |
| **Docker frontend cannot reach the API** | Known limitation (see note below). The Docker frontend image bakes `VITE_API_BASE_URL=http://localhost:8000/api/v1`, so the browser calls the backend directly instead of going through Nginx. To make the Nginx `/api/` proxy work, set `ENV VITE_API_BASE_URL=/api/v1` in `docker/frontend.Dockerfile` before `RUN npm run build` and rebuild the frontend image. This is a behavior change and must be approved before applying. |
| Port already in use (3001/8001/5433) | Check the current configuration; do not change occupied host ports. |

---

## 17. Security & Repository Hygiene

- **Never commit `.env` files, `data/raw/*.csv`, or credentials to Git.**
- Default credentials (`Admin123!`) are for local development only - change the
  `SECRET_KEY` and admin password for any shared deployment.
- The Olist dataset has no product cost/discount fields, so profit and discount
  impact are not presented as real results.
- Engagement risk is rule-based, not a trained churn-prediction model.

---

## 18. License

MIT - see [`LICENSE`](./LICENSE).
