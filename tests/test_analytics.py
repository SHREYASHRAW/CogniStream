from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest

from backend.app.services import analytics


def test_get_developer_activity_returns_grouped_results():
    mock_client = MagicMock()

    mock_client.query.return_value.result_rows = [
        ("developer_01", "team_01", "github", 8),
        ("developer_01", "team_01", "ide", 10),
        ("developer_01", "team_01", "jira", 5),
        ("developer_01", "team_01", "slack", 6),
        ("developer_05", "team_02", "github", 12),
        ("developer_05", "team_02", "ide", 16),
    ]

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_developer_activity()

    assert len(result) == 2

    # Developer 01 has 29 events, so should appear first.
    assert result[0]["developer_id"] == "developer_01"
    assert result[0]["team_id"] == "team_01"
    assert result[0]["total_events"] == 29

    # Developer 05 has 28 events, so should appear second.
    assert result[1]["developer_id"] == "developer_05"
    assert result[1]["team_id"] == "team_02"
    assert result[1]["total_events"] == 28

    assert len(result[0]["events_by_source"]) == 4
    assert len(result[1]["events_by_source"]) == 2

    mock_client.close.assert_called_once()


def test_get_developer_activity_returns_empty_list():
    mock_client = MagicMock()
    mock_client.query.return_value.result_rows = []

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_developer_activity()

    assert result == []
    mock_client.close.assert_called_once()


def test_get_developer_activity_closes_client_on_query_failure():
    mock_client = MagicMock()
    mock_client.query.side_effect = RuntimeError("Simulated query failure")

    with (
        patch.object(
            analytics,
            "get_clickhouse_client",
            return_value=mock_client,
        ),
        pytest.raises(RuntimeError, match="Simulated query failure"),
    ):
        analytics.get_developer_activity()

    mock_client.close.assert_called_once()


def test_get_event_trends_returns_iso_timestamps():
    mock_client = MagicMock()

    timestamp = datetime(
        2026, 10, 17, 10, 0, tzinfo=timezone.utc
    )

    mock_client.query.return_value.result_rows = [
        (timestamp, 15),
    ]

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_event_trends()

    assert result == [
        {
            "timestamp": "2026-10-17T10:00:00+00:00",
            "event_count": 15,
        }
    ]

    mock_client.close.assert_called_once()


def test_get_source_activity_returns_formatted_results():
    mock_client = MagicMock()

    first_event = datetime(
        2026, 10, 16, 13, 0, tzinfo=timezone.utc
    )
    last_event = datetime(
        2026, 10, 17, 12, 0, tzinfo=timezone.utc
    )

    mock_client.query.return_value.result_rows = [
        ("github", 30, 5, first_event, last_event),
        ("slack", 30, 5, first_event, last_event),
    ]

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_source_activity()

    assert len(result) == 2

    assert result[0] == {
        "source": "github",
        "total_events": 30,
        "active_developers": 5,
        "first_event": first_event.isoformat(),
        "last_event": last_event.isoformat(),
    }

    assert result[1]["source"] == "slack"
    assert result[1]["total_events"] == 30

    mock_client.close.assert_called_once()


def test_get_source_activity_returns_empty_list():
    mock_client = MagicMock()
    mock_client.query.return_value.result_rows = []

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_source_activity()

    assert result == []
    mock_client.close.assert_called_once()


def test_get_context_switches_returns_formatted_results():
    mock_client = MagicMock()

    previous_timestamp = datetime(
        2026, 10, 16, 15, 47, 5, 188000
    )
    current_timestamp = datetime(
        2026, 10, 16, 16, 3, 10, 352000
    )

    mock_client.query.return_value.result_rows = [
        (
            "developer_01",
            "team_01",
            "ide",
            "jira",
            previous_timestamp,
            current_timestamp,
            965,
        ),
    ]

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_context_switches()

    assert result == [
        {
            "developer_id": "developer_01",
            "team_id": "team_01",
            "previous_source": "ide",
            "current_source": "jira",
            "previous_timestamp": previous_timestamp.isoformat(),
            "current_timestamp": current_timestamp.isoformat(),
            "gap_seconds": 965,
        }
    ]

    # Confirm that the SQL file was executed.
    mock_client.query.assert_called_once()
    mock_client.close.assert_called_once()


def test_get_context_switches_returns_empty_list():
    mock_client = MagicMock()
    mock_client.query.return_value.result_rows = []

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_context_switches()

    assert result == []
    mock_client.close.assert_called_once()


def test_get_context_switches_closes_client_on_query_failure():
    mock_client = MagicMock()
    mock_client.query.side_effect = RuntimeError(
        "Simulated context-switch query failure"
    )

    with (
        patch.object(
            analytics,
            "get_clickhouse_client",
            return_value=mock_client,
        ),
        pytest.raises(
            RuntimeError,
            match="Simulated context-switch query failure",
        ),
    ):
        analytics.get_context_switches()

    mock_client.close.assert_called_once()


def test_get_developer_transition_summary_returns_formatted_results():
    mock_client = MagicMock()

    mock_client.query.return_value.result_rows = [
        (
            "developer_01",
            "team_01",
            27,
            14,
            13,
            2744.4,
            126,
            18954,
        ),
        (
            "developer_05",
            "team_02",
            22,
            11,
            11,
            2900.7,
            30,
            10319,
        ),
    ]

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_developer_transition_summary()

    assert len(result) == 2

    assert result[0] == {
        "developer_id": "developer_01",
        "team_id": "team_01",
        "total_transitions": 27,
        "short_gap_transitions": 14,
        "long_gap_transitions": 13,
        "avg_gap_seconds": 2744.4,
        "min_gap_seconds": 126,
        "max_gap_seconds": 18954,
    }

    assert result[1]["developer_id"] == "developer_05"
    assert result[1]["total_transitions"] == 22

    mock_client.query.assert_called_once()
    mock_client.close.assert_called_once()


def test_get_developer_transition_summary_returns_empty_list():
    mock_client = MagicMock()
    mock_client.query.return_value.result_rows = []

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_developer_transition_summary()

    assert result == []
    mock_client.close.assert_called_once()


def test_get_developer_transition_summary_closes_client_on_query_failure():
    mock_client = MagicMock()
    mock_client.query.side_effect = RuntimeError(
        "Simulated developer transition query failure"
    )

    with (
        patch.object(
            analytics,
            "get_clickhouse_client",
            return_value=mock_client,
        ),
        pytest.raises(
            RuntimeError,
            match="Simulated developer transition query failure",
        ),
    ):
        analytics.get_developer_transition_summary()

    mock_client.close.assert_called_once()


def test_get_transition_summary_returns_formatted_results():
    mock_client = MagicMock()

    mock_client.query.return_value.result_rows = [
        (
            "team_01",
            "github",
            "slack",
            12,
            5,
            7,
            3200.5,
            120,
            9000,
        ),
        (
            "team_02",
            "ide",
            "jira",
            8,
            4,
            4,
            2500.0,
            300,
            6000,
        ),
    ]

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_transition_summary()

    assert len(result) == 2

    assert result[0] == {
        "team_id": "team_01",
        "previous_source": "github",
        "current_source": "slack",
        "total_transitions": 12,
        "short_gap_transitions": 5,
        "long_gap_transitions": 7,
        "avg_gap_seconds": 3200.5,
        "min_gap_seconds": 120,
        "max_gap_seconds": 9000,
    }

    assert result[1]["team_id"] == "team_02"
    assert result[1]["total_transitions"] == 8

    mock_client.query.assert_called_once()
    mock_client.close.assert_called_once()


def test_get_transition_summary_returns_empty_list():
    mock_client = MagicMock()
    mock_client.query.return_value.result_rows = []

    with patch.object(
        analytics,
        "get_clickhouse_client",
        return_value=mock_client,
    ):
        result = analytics.get_transition_summary()

    assert result == []
    mock_client.close.assert_called_once()


def test_get_transition_summary_closes_client_on_query_failure():
    mock_client = MagicMock()
    mock_client.query.side_effect = RuntimeError(
        "Simulated transition summary query failure"
    )

    with (
        patch.object(
            analytics,
            "get_clickhouse_client",
            return_value=mock_client,
        ),
        pytest.raises(
            RuntimeError,
            match="Simulated transition summary query failure",
        ),
    ):
        analytics.get_transition_summary()

    mock_client.close.assert_called_once()