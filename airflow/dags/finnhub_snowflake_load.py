from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email_on_retry": False,
}

# S3 path (relative to stage root) → Snowflake table name
# Matches your working copy_into.sql exactly
ENDPOINT_TABLE_MAP = {
    "bronze/company_profile2": "company_profile_raw",
    "bronze/basic_financials": "basic_financials_raw",
    "bronze/earnings":         "eps_surprises_raw",
    "bronze/senate_lobbying":  "lobbying_raw",
    "bronze/usa_spending":     "usa_spending_raw",
}

with DAG(
    dag_id="finnhub_snowflake_load",
    description="Load S3 bronze NDJSON → Snowflake finnhub.finnhub_bronze raw tables",
    schedule=None,
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["silver", "snowflake", "elt"],
) as dag:

    start = EmptyOperator(task_id="start")

    load_tasks = []
    for endpoint, table in ENDPOINT_TABLE_MAP.items():
        task = SnowflakeOperator(
            task_id=f"load_{table}",
            snowflake_conn_id="snowflake_default",
            sql=f"""
                COPY INTO finnhub.finnhub_bronze.{table} (ticker, pulled_at, data)
                FROM (
                    SELECT
                        $1:ticker::VARCHAR,
                        $1:pulled_at::DATE,
                        $1:data::VARIANT
                    FROM @finnhub.finnhub_bronze.s3_bronze_stage/{endpoint}/
                )
                FILE_FORMAT = (TYPE = 'JSON')
                ON_ERROR = 'CONTINUE';
            """,
        )
        load_tasks.append(task)

    end = EmptyOperator(task_id="end")

    trigger_silver = TriggerDagRunOperator(
        task_id="trigger_dbt_silver",
        trigger_dag_id="finnhub_dbt_silver",
        wait_for_completion=False,
    )

    start >> load_tasks >> end >> trigger_silver