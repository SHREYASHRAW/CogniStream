
import json

import pytest

from processing import combine_events


@pytest.fixture
def sample_events(tmp_path, monkeypatch):
    """Create isolated mock event files for testing."""
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()

    events_by_source = {
        "github_events.jsonl": [
            {
                "event_id": "test_001",
                "source": "github",
                "event_type": "push",
                "developer_id": "developer_01",
                "team_id": "team_01",
                "timestamp": "2026-10-18T10:00:00Z",
                "metadata": {"repository": "demo", "commits": 2},
            }
        ],
        "slack_events.jsonl": [
            {
                "event_id": "test_002",
                "source": "slack",
                "event_type": "message",
                "developer_id": "developer_01",
                "team_id": "team_01",
                "timestamp": "2026-10-18T10:05:00Z",
                "metadata": {"channel": "engineering"},
            }
        ],
        "jira_events.jsonl": [
            {
                "event_id": "test_003",
                "source": "jira",
                "event_type": "issue_updated",
                "developer_id": "developer_02",
                "team_id": "team_01",
                "timestamp": "2026-10-18T10:10:00Z",
                "metadata": {"issue": "COG-101"},
            }
        ],
        "ide_events.jsonl": [
            {
                "event_id": "test_004",
                "source": "ide",
                "event_type": "file_saved",
                "developer_id": "developer_02",
                "team_id": "team_01",
                "timestamp": "2026-10-18T10:15:00Z",
                "metadata": {"language": "python"},
            }
        ],
    }

    for filename, events in events_by_source.items():
        file_path = raw_dir / filename
        file_path.write_text(
            "\n".join(json.dumps(event) for event in events) + "\n",
            encoding="utf-8",
        )

    monkeypatch.setattr(combine_events, "RAW_DIR", raw_dir)
    return raw_dir


def test_load_events_reads_all_sources(sample_events):
    records = combine_events.load_events()

    assert len(records) == 4
    assert {record["source"] for record in records} == {
        "github",
        "slack",
        "jira",
        "ide",
    }


def test_load_events_preserves_event_fields(sample_events):
    records = combine_events.load_events()
    event = next(record for record in records if record["event_id"] == "test_001")

    assert event["developer_id"] == "developer_01"
    assert event["team_id"] == "team_01"
    assert json.loads(event["metadata_json"]) == {
        "commits": 2,
        "repository": "demo",
    }


def test_load_events_skips_blank_lines(sample_events):
    file_path = sample_events / "github_events.jsonl"
    original_content = file_path.read_text(encoding="utf-8")
    file_path.write_text("\n" + original_content + "\n\n", encoding="utf-8")

    records = combine_events.load_events()

    assert len(records) == 4


def test_load_events_fails_when_input_file_is_missing(
    sample_events, monkeypatch
):
    missing_files = [
        "github_events.jsonl",
        "slack_events.jsonl",
        "jira_events.jsonl",
        "ide_events.jsonl",
    ]
    missing_file = sample_events / missing_files[0]
    missing_file.unlink()

    with pytest.raises(FileNotFoundError, match="Required input file not found"):
        combine_events.load_events()


def test_load_events_fails_on_invalid_json(sample_events):
    file_path = sample_events / "github_events.jsonl"
    file_path.write_text('{"event_id": "broken"\n', encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid JSON"):
        combine_events.load_events()

import polars as pl


def test_main_creates_sorted_parquet_output(sample_events, monkeypatch, tmp_path):
    output_file = tmp_path / "processed" / "all_events.parquet"
    monkeypatch.setattr(combine_events, "OUTPUT_FILE", output_file)

    combine_events.main()

    assert output_file.exists()

    df = pl.read_parquet(output_file)

    assert df.height == 4
    assert set(combine_events.REQUIRED_COLUMNS).issubset(df.columns)
    assert df["event_id"].n_unique() == 4
    assert df["timestamp"].is_sorted()
    assert df["timestamp"].dtype == pl.Datetime(
        time_unit="us", time_zone="UTC"
    )
