
from datetime import datetime

from airflow import DAG
from airflow.operators.bash import BashOperator


PROJECT_DIR = "/opt/airflow/project"

COMMON_ENV = {
    "PYTHONPATH": PROJECT_DIR,
    "DBT_PROFILES_DIR": f"{PROJECT_DIR}/docker",
    "ECOMMERCE_DUCKDB_PATH": (
        f"{PROJECT_DIR}/data/warehouse/ecommerce.duckdb"
    ),
}


with DAG(
    dag_id="olist_data_pipeline",
    description="Orchestrate the Olist ETL, data quality, observability and dbt transformations",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["olist", "data-engineering", "observability"],
) as dag:

    # Task 1: Transform Bronze data into Silver data
    bronze_to_silver = BashOperator(
        task_id="bronze_to_silver",
        bash_command="python -m src.etl.bronze_to_silver",
        cwd=PROJECT_DIR,
        env=COMMON_ENV,
        append_env=True,
    )

    # Task 2: Generate the data quality report
    data_quality = BashOperator(
        task_id="data_quality",
        bash_command="python -m src.quality.generate_quality_report",
        cwd=PROJECT_DIR,
        env=COMMON_ENV,
        append_env=True,
    )

    # Task 3: Record quality metrics in the historical CSV
    track_quality_metrics = BashOperator(
        task_id="track_quality_metrics",
        bash_command="python -m src.observability.track_quality_metrics",
        cwd=PROJECT_DIR,
        env=COMMON_ENV,
        append_env=True,
    )

    # Task 4: Run dbt transformations and tests
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command="/opt/airflow/dbt-venv/bin/dbt build --project-dir dbt",
        cwd=PROJECT_DIR,
        env=COMMON_ENV,
        append_env=True,
    )

    # Define execution order
    bronze_to_silver >> data_quality >> track_quality_metrics >> dbt_build
