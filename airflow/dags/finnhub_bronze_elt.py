# finnhub_bronze_elt.py
import sys
import os
import logging
from datetime import datetime, timedelta

sys.path.insert(0, '/opt/airflow')

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator

logger = logging.getLogger(__name__)

# ── Callables defined at module level (NOT instantiated here) ──────────────────
# Each function creates its pipeline object only when Airflow actually runs
# the task. This prevents heavy __init__ work (boto3 clients, finnhub.Client)
# from executing on every DAG parse cycle.

def run_company_profile():
    from pipelines.company_profile_pipeline import CompanyProfilePipeline
    CompanyProfilePipeline().run()

def run_basic_financials():
    from pipelines.basic_financials_pipeline import BasicFinancialsPipeline
    BasicFinancialsPipeline().run()

def run_earnings():
    from pipelines.earnings_pipeline import EarningsPipeline
    EarningsPipeline().run()

def run_lobbying():
    from pipelines.lobbying_pipeline import LobbyingPipeline
    LobbyingPipeline().run()

def run_usa_spending():
    from pipelines.usa_spending_pipeline import USASpendingPipeline
    USASpendingPipeline().run()


# ── Default args applied to every task ────────────────────────────────────────
default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,           # each daily run is independent
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,                       # Airflow-level task retry (separate from
    "retry_delay": timedelta(minutes=5) # fetch_with_retry inside BasePipeline)
}

# ── DAG definition ─────────────────────────────────────────────────────────────
with DAG(
    dag_id="finnhub_bronze_elt",
    description="Ingest Finnhub + gov data → validate → S3 bronze layer",
    schedule="0 6 * * 1-5",            # 06:00 UTC, weekdays only
    start_date=datetime(2024, 1, 1),
    catchup=False,                      # don't back-fill missed runs
    default_args=default_args,
    tags=["bronze", "finnhub", "etl"],
) as dag:

    start = EmptyOperator(task_id="start")

    company_profile = PythonOperator(
        task_id="company_profile",
        python_callable=run_company_profile,
    )

    basic_financials = PythonOperator(
        task_id="basic_financials",
        python_callable=run_basic_financials,
    )

    earnings = PythonOperator(
        task_id="earnings",
        python_callable=run_earnings,
    )

    lobbying = PythonOperator(
        task_id="lobbying",
        python_callable=run_lobbying,
    )

    usa_spending = PythonOperator(
        task_id="usa_spending",
        python_callable=run_usa_spending,
    )

    # All five tasks complete before downstream silver/gold layers can trigger
    end = EmptyOperator(task_id="log_pipeline_summary")

    # ── Dependency graph ───────────────────────────────────────────────────────
    # start fans out to all five in parallel; all five fan in to end.
    # The pipelines have no inter-dependencies, so no ordering between them.
    start >> company_profile >> basic_financials >> earnings >> lobbying >> usa_spending >> end

    from airflow.operators.trigger_dagrun import TriggerDagRunOperator

# inside your existing DAG block, after your existing tasks:

    trigger_snowflake_load = TriggerDagRunOperator(
        task_id="trigger_snowflake_load",
        trigger_dag_id="finnhub_snowflake_load",
        wait_for_completion=False,  # bronze DAG doesn't wait for snowflake to finish
    )

    # update your dependency chain:
    start >> company_profile >> basic_financials >> earnings >> lobbying >> usa_spending >> end >> trigger_snowflake_load