# Platform Architecture & System Design

## 1. High-Level Architecture Overview

```mermaid
flowchart TD
    subgraph Client ["Client Layer"]
        Browser["React 18 + TypeScript SPA<br/>(Tailwind CSS, Recharts, Vite)"]
    end

    subgraph Gateway ["Reverse Proxy & Ingress"]
        Nginx["Nginx Reverse Proxy<br/>Port 3000 / Port 80"]
    end

    subgraph AppServer ["Application Backend (FastAPI)"]
        Router["FastAPI REST Router<br/>(/api/v1)"]
        AuthSvc["Auth Service & JWT"]
        HealthSvc["Health & Telemetry"]
        DQService["Data Quality Audit Service"]
        ETL["ETL & Ingestion Pipeline<br/>(Pandas, Chunks)"]
    end

    subgraph DataLayer ["Data & Storage Layer"]
        PG[("PostgreSQL 16 Relational Engine<br/>9 Olist Tables + Users")]
        RawData["data/raw/<br/>(Immutable CSV Source Files)"]
        ProcData["data/processed/<br/>(Normalized Outputs)"]
    end

    Browser -->|HTTP/REST| Nginx
    Nginx -->|Proxy /api/| Router
    Router --> AuthSvc
    Router --> HealthSvc
    Router --> DQService
    AuthSvc --> PG
    HealthSvc --> PG
    DQService --> PG
    DQService --> RawData
    ETL --> RawData
    ETL --> PG
    ETL --> ProcData
```

## 2. Core Architectural Principles
1. **Raw Data Immutability**: All source CSVs downloaded from Olist are treated as read-only, write-once immutable artifacts.
2. **Strict Separation of Concerns**: React components never perform business calculations or database queries; they communicate via typed REST interfaces.
3. **No Fabricated / Simulated Metrics**: Dashboards reflect true schema metadata, verified table row counts, and null rates calculated directly from SQL queries.
4. **Relational Integrity**: Foreign keys, composite primary keys, and cascade deletion rules safeguard dataset consistency.
5. **Horizontal & Modular Scalability**: Analytical algorithms (RFM, Churn, Forecasting) plug directly into modular service directories in upcoming pipeline stages.
