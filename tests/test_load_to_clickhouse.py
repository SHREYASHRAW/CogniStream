
from unittest.mock import MagicMock, patch

import polars as pl
import pytest

from processing import load_to_clickhouse as loader


def sample_events():
    return pl.DataFrame(
        {
            "event_id": ["event_001", "event_002", "event_003"],
            "source": ["github", "slack", "jira"],
            "event_type": ["push", "message", "issue"],
            "developer_id": ["dev_01", "dev_02", "dev_03"],
            "team_id": ["team_01", "team_01", "team_02"],
            "timestamp": [
                "2026-10-17T10:00:00+00:00",
                "2026-10-17T10:05:00+00:00",
                "2026-10-17T10:10:00+00:00",
            ],
            "metadata_json": ['{"action":"push"}', '{"action":"post"}', '{"action":"open"}'],
        }
    ).with_columns(pl.col("timestamp").str.to_datetime(time_zone="UTC"))


def mock_client(existing_ids=None):
    client = MagicMock()
    client.query.return_value.result_rows = [
        (event_id,) for event_id in (existing_ids or [])
    ]
    return client


def test_missing_parquet_file_raises_error(tmp_path):
    missing_file = tmp_path / "missing.parquet"

    with patch.object(loader, "PARQUET_FILE", missing_file):
        with pytest.raises(FileNotFoundError, match="Processed Parquet file not found"):
            loader.load_to_clickhouse()


def test_missing_required_column_raises_error(tmp_path):
    parquet_file = tmp_path / "events.parquet"
    sample_events().drop("source").write_parquet(parquet_file)

    with (
        patch.object(loader, "PARQUET_FILE", parquet_file),
        pytest.raises(ValueError, match="Missing required columns"),
        patch.object(loader, "create_client") as create_client,
    ):
        loader.load_to_clickhouse()

    create_client.assert_not_called()


def test_empty_dataset_raises_error(tmp_path):
    parquet_file = tmp_path / "events.parquet"
    sample_events().head(0).write_parquet(parquet_file)

    with (
        patch.object(loader, "PARQUET_FILE", parquet_file),
        pytest.raises(ValueError, match="contains no events"),
        patch.object(loader, "create_client") as create_client,
    ):
        loader.load_to_clickhouse()

    create_client.assert_not_called()


def test_null_event_id_raises_error(tmp_path):
    parquet_file = tmp_path / "events.parquet"
    sample_events().with_columns(
        pl.when(pl.int_range(pl.len()) == 0)
        .then(None)
        .otherwise(pl.col("event_id"))
        .alias("event_id")
    ).write_parquet(parquet_file)

    with (
        patch.object(loader, "PARQUET_FILE", parquet_file),
        pytest.raises(ValueError, match="null event IDs"),
        patch.object(loader, "create_client") as create_client,
    ):
        loader.load_to_clickhouse()

    create_client.assert_not_called()


def test_duplicate_event_ids_raise_error(tmp_path):
    parquet_file = tmp_path / "events.parquet"
    sample_events().with_columns(
        pl.lit("duplicate_id").alias("event_id")
    ).write_parquet(parquet_file)

    with (
        patch.object(loader, "PARQUET_FILE", parquet_file),
        pytest.raises(ValueError, match="duplicate event IDs"),
        patch.object(loader, "create_client") as create_client,
    ):
        loader.load_to_clickhouse()

    create_client.assert_not_called()


def test_only_new_events_are_inserted(tmp_path):
    parquet_file = tmp_path / "events.parquet"
    sample_events().write_parquet(parquet_file)
    client = mock_client(existing_ids=["event_001", "event_003"])

    with (
        patch.object(loader, "PARQUET_FILE", parquet_file),
        patch.object(loader, "create_client", return_value=client),
        patch("builtins.print") as mock_print,
    ):
        loader.load_to_clickhouse()

    client.query.assert_called_once_with(
        "SELECT event_id FROM developer_events"
    )
    client.insert_df.assert_called_once()

    args, kwargs = client.insert_df.call_args
    assert args[0] == "developer_events"
    assert set(args[1]["event_id"]) == {"event_002"}
    assert kwargs["database"] == "cognistream"

    printed_output = " ".join(
        str(call.args[0]) for call in mock_print.call_args_list
    )
    assert "Parquet rows: 3" in printed_output
    assert "Already present: 2" in printed_output
    assert "Inserted: 1" in printed_output
    client.close.assert_called_once()


def test_no_insert_when_all_events_already_exist(tmp_path):
    parquet_file = tmp_path / "events.parquet"
    sample_events().write_parquet(parquet_file)
    client = mock_client(
        existing_ids=["event_001", "event_002", "event_003"]
    )

    with patch.object(loader, "PARQUET_FILE", parquet_file), patch.object(
        loader, "create_client", return_value=client
    ):
        loader.load_to_clickhouse()

    client.insert_df.assert_not_called()
    client.close.assert_called_once()


def test_client_closes_when_query_fails(tmp_path):
    parquet_file = tmp_path / "events.parquet"
    sample_events().write_parquet(parquet_file)
    client = mock_client()
    client.query.side_effect = RuntimeError("Simulated query failure")

    with (
        patch.object(loader, "PARQUET_FILE", parquet_file),
        patch.object(loader, "create_client", return_value=client),
        pytest.raises(RuntimeError, match="Simulated query failure"),
    ):
        loader.load_to_clickhouse()

    client.close.assert_called_once()
