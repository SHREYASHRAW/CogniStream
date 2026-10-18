
import polars as pl


EXPECTED_SOURCES = {"github", "slack", "jira", "ide"}

REQUIRED_COLUMNS = {
    "event_id",
    "source",
    "event_type",
    "developer_id",
    "team_id",
    "timestamp",
    "metadata_json",
}


def test_processed_dataset_has_required_columns():
    df = pl.read_parquet("data/processed/all_events.parquet")

    assert REQUIRED_COLUMNS.issubset(set(df.columns))


def test_processed_dataset_has_unique_event_ids():
    df = pl.read_parquet("data/processed/all_events.parquet")

    assert df["event_id"].n_unique() == df.height


def test_processed_dataset_has_no_empty_identifiers():
    df = pl.read_parquet("data/processed/all_events.parquet")

    assert df.filter(
        pl.col("developer_id").is_null()
        | (pl.col("developer_id").str.strip_chars() == "")
        | pl.col("team_id").is_null()
        | (pl.col("team_id").str.strip_chars() == "")
    ).height == 0


def test_processed_dataset_has_expected_sources():
    df = pl.read_parquet("data/processed/all_events.parquet")

    assert set(df["source"].unique().to_list()) == EXPECTED_SOURCES


def test_processed_dataset_has_valid_sorted_timestamps():
    df = pl.read_parquet("data/processed/all_events.parquet")

    assert df["timestamp"].null_count() == 0
    assert df["timestamp"].is_sorted()
