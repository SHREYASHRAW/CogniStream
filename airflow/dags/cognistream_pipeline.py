
from datetime import datetime, timedelta
import os
import subprocess
import sys
from pathlib import Path

from airflow import DAG
from airflow.operators.python import PythonOperator


PROJECT_ROOT = Path(
    os.getenv("COGNISTREAM_PROJECT_ROOT", "/opt/cognistream")
)

PYTHON_EXECUTABLE = sys.executable


def run_project_script(script_relative_path: str) -> None:
    """Run a project script and fail the Airflow task on errors."""
    script_path = PROJECT_ROOT / script_relative_path

    if not script_path.is_file():
        raise FileNotFoundError(
            f"CogniStream script not found: {script_path}"
        )

    result = subprocess.run(
        [PYTHON_EXECUTABLE, str(script_path)],
        cwd=str(PROJECT_ROOT),
        check=False,
        capture_output=True,
        text=True,
    )

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(
            f"Script failed with exit code {result.returncode}: "
            f"{script_path}"
        )


def validate_raw_events() -> None:
    run_project_script("ingestion/schemas/validate_events.py")


def combine_events() -> None:
    run_project_script("processing/combine_events.py")


def load_events() -> None:
    run_project_script("processing/load_to_clickhouse.py")


def verify_clickhouse_load() -> None:
    """Verify that ClickHouse contains events after the load task."""
    import clickhouse_connect

    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "host.docker.internal"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "cogni"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DATABASE", "cognistream"),
    )

    try:
        result = client.query(
            """
            SELECT
                count() AS total_rows,
                uniqExact(event_id) AS unique_event_ids
            FROM developer_events
            """
        )
        total_rows, unique_event_ids = result.result_rows[0]

        print(f"ClickHouse rows: {total_rows}")
        print(f"Unique event IDs: {unique_event_ids}")

        if total_rows != unique_event_ids:
            raise ValueError(
                "ClickHouse contains duplicate event IDs: "
                f"{total_rows} rows, {unique_event_ids} unique IDs"
            )

        if total_rows == 0:
            raise ValueError("ClickHouse contains no events.")

    finally:
        client.close()


default_args = {
    "owner": "cognistream",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="cognistream_pipeline",
    description="Validate, process, load, and verify CogniStream events",
    default_args=default_args,
    start_date=datetime(2026, 10, 20),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    tags=["cognistream", "data-pipeline"],
) as dag:
    validate_events_task = PythonOperator(
        task_id="validate_raw_events",
        python_callable=validate_raw_events,
    )

    combine_events_task = PythonOperator(
        task_id="combine_events_to_parquet",
        python_callable=combine_events,
    )

    load_events_task = PythonOperator(
        task_id="load_events_to_clickhouse",
        python_callable=load_events,
    )

    verify_events_task = PythonOperator(
        task_id="verify_clickhouse_load",
        python_callable=verify_clickhouse_load,
    )

    (
        validate_events_task
        >> combine_events_task
        >> load_events_task
        >> verify_events_task
    )
