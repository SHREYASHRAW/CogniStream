
import os
from pathlib import Path

import clickhouse_connect
import polars as pl
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

PARQUET_FILE = PROJECT_ROOT / "data" / "processed" / "all_events.parquet"

REQUIRED_COLUMNS = [
    "event_id",
    "source",
    "event_type",
    "developer_id",
    "team_id",
    "timestamp",
    "metadata_json",
]


def create_client():
    return clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "localhost"),
        port=int(os.getenv("CLICKHOUSE_PORT", "8123")),
        username=os.getenv("CLICKHOUSE_USER", "default"),
        password=os.getenv("CLICKHOUSE_PASSWORD", ""),
        database=os.getenv("CLICKHOUSE_DATABASE", "cognistream"),
    )


def load_to_clickhouse():
    if not PARQUET_FILE.exists():
        raise FileNotFoundError(
            f"Processed Parquet file not found: {PARQUET_FILE}"
        )

    df = pl.read_parquet(PARQUET_FILE)

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    df = df.select(REQUIRED_COLUMNS)

    if df.is_empty():
        raise ValueError("The Parquet dataset contains no events.")

    if df["event_id"].null_count() > 0:
        raise ValueError("The dataset contains null event IDs.")

    if df["event_id"].n_unique() != df.height:
        raise ValueError("The dataset contains duplicate event IDs.")

    client = create_client()

    try:
        existing_result = client.query(
            "SELECT event_id FROM developer_events"
        )
        existing_ids = {row[0] for row in existing_result.result_rows}

        missing_df = df.filter(
            ~pl.col("event_id").is_in(list(existing_ids))
        )

        if missing_df.height > 0:
            client.insert_df(
                "developer_events",
                missing_df.to_pandas(),
                database="cognistream",
            )

        print(f"Parquet rows: {df.height}")
        print(f"Already present: {df.height - missing_df.height}")
        print(f"Inserted: {missing_df.height}")

    finally:
        client.close()


def main():
    load_to_clickhouse()


if __name__ == "__main__":
    main()
