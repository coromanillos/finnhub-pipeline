# dags/data_pipeline_dag.py
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from pipelines.company_profile_pipeline import CompanyProfilePipeline
from pipelines.basic_financials_pipeline import BasicFinancialsPipeline
from pipelines.earnings_pipeline import EarningsPipeline
from pipelines.lobbying_pipeline import LobbyingPipeline
from pipelines.usa_spending_pipeline import USASpendingPipeline

default_args = {
    'owner': 'data_team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def run_pipeline(pipeline_class, endpoint_name, **context):
    """Generic function to run a pipeline."""
    pipeline = pipeline_class()
    try:
        pipeline.run()
        return f"{endpoint_name} completed"
    except Exception as e:
        raise Exception(f"{endpoint_name} failed: {str(e)}")

with DAG(
    'data_pipeline_dag',
    default_args=default_args,
    description='Main data ingestion DAG',
    schedule_interval='@daily',  # Run daily
    catchup=False,
    tags=['data_pipeline'],
) as dag:
    
    # Start marker
    start = DummyOperator(task_id='start')
    
    # Define tasks
    company_profile = PythonOperator(
        task_id='company_profile',
        python_callable=run_pipeline,
        op_kwargs={
            'pipeline_class': CompanyProfilePipeline,
            'endpoint_name': 'company_profile'
        }
    )
    
    basic_financials = PythonOperator(
        task_id='basic_financials',
        python_callable=run_pipeline,
        op_kwargs={
            'pipeline_class': BasicFinancialsPipeline,
            'endpoint_name': 'basic_financials'
        }
    )
    
    earnings = PythonOperator(
        task_id='earnings',
        python_callable=run_pipeline,
        op_kwargs={
            'pipeline_class': EarningsPipeline,
            'endpoint_name': 'earnings'
        }
    )
    
    lobbying = PythonOperator(
        task_id='lobbying',
        python_callable=run_pipeline,
        op_kwargs={
            'pipeline_class': LobbyingPipeline,
            'endpoint_name': 'lobbying'
        }
    )
    
    usa_spending = PythonOperator(
        task_id='usa_spending',
        python_callable=run_pipeline,
        op_kwargs={
            'pipeline_class': USASpendingPipeline,
            'endpoint_name': 'usa_spending'
        }
    )
    
    # End marker
    end = DummyOperator(task_id='end')
    
    # Define dependencies (the DAG structure)
    start >> company_profile
    
    # These three run in parallel after company_profile
    company_profile >> [basic_financials, earnings, lobbying]
    
    # usa_spending requires both basic_financials and lobbying
    [basic_financials, lobbying] >> usa_spending
    
    usa_spending >> end