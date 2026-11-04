from datetime import datetime, timedelta

from airflow.providers.standard.operators.bash import BashOperator
from airflow.sdk import DAG

PROJECT = "/opt/project"
DBT_BIN = "/home/airflow/dbt_venv/bin/dbt"

default_args = {
    "owner": "emiliano",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="football_pipeline",
    description="Ingest football-data.org -> load raw layer -> dbt build",
    start_date=datetime(2026, 11, 1),
    schedule="0 6 * * *",  # every day at 06:00
    catchup=False,
    default_args=default_args,
    tags=["football", "elt"],
) as dag:
    ingest = BashOperator(
        task_id="ingest",
        bash_command=f"cd {PROJECT} && python -m src.ingest.ingest_matches",
    )
    load_raw = BashOperator(
        task_id="load_raw",
        bash_command=f"cd {PROJECT} && python -m src.load.load_raw",
    )
    dbt_build = BashOperator(
        task_id="dbt_build",
        bash_command=(
            f"cd {PROJECT}/dbt && "
            f"DBT_TARGET_PATH=/tmp/dbt_target DBT_LOG_PATH=/tmp/dbt_logs "
            f"{DBT_BIN} build --profiles-dir ."
        ),
    )

    ingest >> load_raw >> dbt_build