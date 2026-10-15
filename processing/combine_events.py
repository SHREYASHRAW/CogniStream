import json
from pathlib import Path

import polars as pl

RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/processed/all_events.parquet")

SOURCE_FILES = [
    "github_events.jsonl",
    "slack_events.jsonl",
    "jira_events.jsonl",
    "ide_events.jsonl",
]

REQUIRED_COLUMNS = [
    "event_id",
    "source",
    "event_type",
    "developer_id",
    "team_id",
    "timestamp",
    "metadata_json",
]

def load_events():
    records = []

    for filename in SOURCE_FILES:
        file_path = RAW_DIR / filename

        if not file_path.exists():
            raise FileNotFoundError(f"Required input file not found: {file_path}")

        with file_path.open("r", encoding="utf-8-sig") as file:
            for line_number, line in enumerate(file, start=1):
                if not line.strip():
                    continue

                try:
                    event = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Invalid JSON in {file_path}, line {line_number}: {error}"
                    ) from error

                records.append({
                    "event_id": event["event_id"],
                    "source": event["source"],
                    "event_type": event["event_type"],
                    "developer_id": event["developer_id"],
                    "team_id": event["team_id"],
                    "timestamp": event["timestamp"],
                    "metadata_json": json.dumps(
                        event["metadata"],
                        ensure_ascii=False,
                        sort_keys=True,
                    ),
                })

    return records

def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    records = load_events()

    if not records:
        raise ValueError("No events found in the input files.")

    df = pl.DataFrame(records)

    df = df.with_columns(
        pl.col("timestamp").str.to_datetime(
            time_zone="UTC",
            strict=True,
        )
    ).sort("timestamp")

    missing_columns = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing_columns:
        raise ValueError(f"Missing output columns: {sorted(missing_columns)}")

    df.write_parquet(OUTPUT_FILE, compression="zstd")

    print(f"Total processed events: {df.height}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Columns: {', '.join(df.columns)}")
    print("\nEvents by source:")

    summary = (
        df.group_by("source")
        .agg(pl.len().alias("event_count"))
        .sort("source")
    )
    print(summary)

    print("\nTimestamp range:")
    print("Earliest:", df["timestamp"].min())
    print("Latest:", df["timestamp"].max())

    print("\nParquet file created successfully.")

if __name__ == "__main__":
    main()
