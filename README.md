# Finnhub Data Pipeline

An automated end-to-end ELT pipeline that ingests financial and government data from REST APIs, validates and stores it in AWS S3, loads it into Snowflake, and transforms it into analytics-ready gold tables via dbt — fully orchestrated by Apache Airflow.

---

## Architecture

```
Finnhub & Gov APIs
    → AWS S3 (bronze)
        → Snowflake finnhub_bronze (raw tables)
            → Snowflake finnhub_silver (dbt views)
                → Snowflake finnhub_gold (dbt tables)
```

---

## Stack

| Layer | Technology |
|---|---|
| Ingestion | Python, Finnhub API, USA Spending API, Senate Lobbying API |
| Validation | Pydantic v2 |
| Data Lake | AWS S3 (NDJSON) |
| Data Warehouse | Snowflake |
| Transformation | dbt-snowflake |
| Orchestration | Apache Airflow 2.9.1 (LocalExecutor) |
| Containerization | Docker, Docker Compose |

---

## Project Structure

```
finnhub-pipeline/
├── airflow/
│   └── dags/
│       ├── finnhub_bronze_elt.py       # APIs → S3
│       ├── finnhub_snowflake_load.py   # S3 → Snowflake raw
│       ├── finnhub_dbt_silver.py       # dbt silver models
│       └── finnhub_dbt_gold.py         # dbt gold models
├── pipelines/
│   ├── company_profile_pipeline.py
│   ├── basic_financials_pipeline.py
│   ├── earnings_pipeline.py
│   ├── lobbying_pipeline.py
│   └── usa_spending_pipeline.py
├── models/
│   ├── company_profile_model.py
│   ├── basic_financials_model.py
│   ├── earnings_model.py
│   ├── lobbying_model.py
│   └── usa_spending_model.py
├── dbt/
│   ├── models/
│   │   ├── silver/
│   │   │   ├── company_profile.sql
│   │   │   ├── basic_financials_metrics.sql
│   │   │   ├── basic_financials_series.sql
│   │   │   ├── eps_surprises.sql
│   │   │   ├── lobbying.sql
│   │   │   └── usa_spending.sql
│   │   └── gold/
│   │       ├── ticker_scorecard.sql
│   │       └── government_dependency.sql
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── dbt_project.yml
│   ├── profiles.yml               # gitignored
│   └── Dockerfile.dbt
├── base_pipeline.py
├── config.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env                           # gitignored
```

---

## Data Sources

| Pipeline | Source | Tickers |
|---|---|---|
| `company_profile` | Finnhub `/stock/profile2` | 60 |
| `basic_financials` | Finnhub `/stock/metric` | 60 |
| `earnings` | Finnhub `/stock/earnings` | 60 |
| `lobbying` | Senate Lobbying Disclosure API | 60 |
| `usa_spending` | USASpending.gov API | 60 |

---

## Snowflake Schema Layout

```
finnhub (database)
├── finnhub_bronze    raw VARIANT tables loaded via COPY INTO from S3
├── finnhub_silver    typed, cleaned dbt views built on bronze
└── finnhub_gold      aggregated dbt tables ready for BI consumption
```

**Gold tables:**
- `ticker_scorecard` — per-ticker financial metrics, EPS history, and company profile
- `government_dependency` — per-ticker lobbying spend and government contract exposure

---

## DAG Chain

```
finnhub_bronze_elt         (schedule: 0 6 * * 1-5)
    company_profile
        → basic_financials
            → earnings
                → lobbying
                    → usa_spending
                        → triggers finnhub_snowflake_load

finnhub_snowflake_load     (triggered by bronze)
    5 parallel COPY INTO tasks
        → triggers finnhub_dbt_silver

finnhub_dbt_silver         (triggered by snowflake_load)
    dbt run --select silver
        → triggers finnhub_dbt_gold

finnhub_dbt_gold           (triggered by dbt_silver)
    dbt run --select gold
```

---

## Setup

### Prerequisites

- Docker and Docker Compose
- AWS account with S3 bucket and IAM role
- Snowflake account with storage integration configured
- Finnhub API key

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd finnhub-pipeline
cp .env.example .env
# fill in all values in .env
```

### 2. Generate Fernet key

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# paste output into AIRFLOW__CORE__FERNET_KEY in .env
```

### 3. Set directory permissions

```bash
mkdir -p airflow/logs airflow/dags airflow/plugins
sudo chown -R 50000:0 airflow/logs airflow/dags airflow/plugins
sudo chown -R $USER:$USER airflow/dags
```

### 4. Build images

```bash
docker compose build
```

### 5. Initialize Airflow

```bash
docker compose run --rm airflow-init
```

### 6. Start all services

```bash
docker compose up -d airflow-webserver airflow-scheduler dbt
```

### 7. Configure Snowflake connection in Airflow UI

Navigate to `http://localhost:8080` → Admin → Connections → Add:

```
Connection Id:   snowflake_default
Connection Type: Snowflake
Account:         <your_account>
Region:          <your_region>
Login:           <your_user>
Password:        <your_password>
Schema:          finnhub_bronze
Warehouse:       finnhub_wh
Database:        finnhub
```

### 8. Unpause all four DAGs and trigger

In the Airflow UI, unpause all four DAGs and trigger `finnhub_bronze_elt` manually. The remaining three DAGs will cascade automatically.

---

## Environment Variables

| Variable | Description |
|---|---|
| `FINNHUB_API_KEY` | Finnhub API key |
| `AWS_ACCESS_KEY_ID` | AWS access key |
| `AWS_SECRET_ACCESS_KEY` | AWS secret key |
| `AWS_REGION` | AWS region |
| `S3_BUCKET` | S3 bucket name |
| `SNOWFLAKE_ACCOUNT` | Snowflake account identifier |
| `SNOWFLAKE_USER` | Snowflake username |
| `SNOWFLAKE_PASS` | Snowflake password |
| `SNOWFLAKE_ROLE` | Snowflake role |
| `AIRFLOW__CORE__FERNET_KEY` | Airflow encryption key |
| `AIRFLOW__WEBSERVER__SECRET_KEY` | Airflow session key |

---

## Dead Letter Handling

Records that fail Pydantic validation or exhaust API retries are routed to a dead letter file in S3 rather than crashing the pipeline:

```
s3://your-bucket/bronze/<endpoint>/dead_letter/<endpoint>_dead_letter_<date>.ndjson
```

Each dead letter record contains the raw API response and the exact validation errors for inspection and reprocessing.

---

## Stopping and Restarting

```bash
# Stop all containers (preserves Airflow metadata)
docker compose down

# Restart
docker compose up -d airflow-webserver airflow-scheduler dbt

# Full reset (wipes Airflow DB — requires re-init)
docker compose down -v
```