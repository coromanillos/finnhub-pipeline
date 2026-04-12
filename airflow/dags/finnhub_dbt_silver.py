from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta
import os

default_args = {
    "owner": "data-engineering",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email_on_retry": False,
}

with DAG(
    dag_id="finnhub_dbt_silver",
    description="Run dbt silver models — Snowflake raw → finnhub_silver views",
    schedule=None,  # triggered by finnhub_snowflake_load
    start_date=datetime(2024, 1, 1),
    catchup=False,
    default_args=default_args,
    tags=["silver", "dbt", "elt"],
) as dag:

    start = EmptyOperator(task_id="start")

    run_silver = DockerOperator(
        task_id="dbt_run_silver",
        image="finnhub-pipeline-dbt",
        command="dbt run --select silver --profiles-dir /usr/app/dbt",
        working_dir="/usr/app/dbt",
        environment={
            "SNOWFLAKE_ACCOUNT": os.environ.get("SNOWFLAKE_ACCOUNT"),
            "SNOWFLAKE_USER": os.environ.get("SNOWFLAKE_USER"),
            "SNOWFLAKE_PASS": os.environ.get("SNOWFLAKE_PASS"),
            "SNOWFLAKE_ROLE": os.environ.get("SNOWFLAKE_ROLE"),
        },
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
        auto_remove=True,
        mount_tmp_dir=False,
    )

    trigger_gold = TriggerDagRunOperator(
        task_id="trigger_dbt_gold",
        trigger_dag_id="finnhub_dbt_gold",
        wait_for_completion=False,
    )

    end = EmptyOperator(task_id="end")

    start >> run_silver >> trigger_gold >> end