
from unittest.mock import patch

from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["name"] == "CogniStream API"
    assert response.json()["status"] == "running"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_analytics_summary_endpoint():
    response = client.get("/api/v1/summary")

    assert response.status_code == 200

    data = response.json()

    assert data["total_events"] == 120
    assert data["unique_developers"] == 5
    assert data["unique_teams"] == 2

    source_counts = {
        item["source"]: item["count"]
        for item in data["events_by_source"]
    }

    assert source_counts == {
        "github": 30,
        "ide": 30,
        "jira": 30,
        "slack": 30,
    }


def test_developer_activity_endpoint():
    mock_data = [
        {
            "developer_id": "developer_01",
            "team_id": "team_01",
            "total_events": 29,
            "events_by_source": [
                {"source": "github", "count": 8},
                {"source": "ide", "count": 10},
                {"source": "jira", "count": 5},
                {"source": "slack", "count": 6},
            ],
        },
        {
            "developer_id": "developer_05",
            "team_id": "team_02",
            "total_events": 28,
            "events_by_source": [
                {"source": "github", "count": 12},
                {"source": "ide", "count": 16},
            ],
        },
    ]

    with patch(
        "backend.app.api.analytics.get_developer_activity",
        return_value=mock_data,
    ):
        response = client.get("/api/v1/developers/activity")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["developer_id"] == "developer_01"
    assert data[0]["total_events"] == 29

    assert data[1]["developer_id"] == "developer_05"
    assert data[1]["total_events"] == 28

    assert len(data[0]["events_by_source"]) == 4
    assert len(data[1]["events_by_source"]) == 2


def test_hourly_trends_endpoint():
    mock_data = [
        {
            "timestamp": "2026-10-17T10:00:00+00:00",
            "event_count": 15,
        },
        {
            "timestamp": "2026-10-17T11:00:00+00:00",
            "event_count": 20,
        },
    ]

    with patch(
        "backend.app.api.analytics.get_event_trends",
        return_value=mock_data,
    ):
        response = client.get("/api/v1/trends/hourly")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["event_count"] == 15
    assert data[1]["event_count"] == 20
    assert data[0]["timestamp"] == "2026-10-17T10:00:00+00:00"


def test_source_activity_endpoint():
    mock_data = [
        {
            "source": "github",
            "total_events": 30,
            "active_developers": 5,
            "first_event": "2026-10-16T13:00:00+00:00",
            "last_event": "2026-10-17T12:00:00+00:00",
        },
        {
            "source": "slack",
            "total_events": 30,
            "active_developers": 5,
            "first_event": "2026-10-16T13:00:00+00:00",
            "last_event": "2026-10-17T12:00:00+00:00",
        },
    ]

    with patch(
        "backend.app.api.analytics.get_source_activity",
        return_value=mock_data,
    ):
        response = client.get("/api/v1/sources/activity")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["source"] == "github"
    assert data[0]["total_events"] == 30
    assert data[0]["active_developers"] == 5

    assert data[1]["source"] == "slack"
    assert data[1]["total_events"] == 30


def test_context_switches_endpoint():
    mock_data = [
        {
            "developer_id": "developer_01",
            "team_id": "team_01",
            "previous_source": "ide",
            "current_source": "jira",
            "previous_timestamp": "2026-10-16T15:47:05.188000",
            "current_timestamp": "2026-10-16T16:03:10.352000",
            "gap_seconds": 965,
        },
        {
            "developer_id": "developer_02",
            "team_id": "team_01",
            "previous_source": "github",
            "current_source": "slack",
            "previous_timestamp": "2026-10-16T14:00:00",
            "current_timestamp": "2026-10-16T14:10:00",
            "gap_seconds": 600,
        },
    ]

    with patch(
        "backend.app.api.analytics.get_context_switches",
        return_value=mock_data,
    ):
        response = client.get("/api/v1/context-switches")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["developer_id"] == "developer_01"
    assert data[0]["previous_source"] == "ide"
    assert data[0]["current_source"] == "jira"
    assert data[0]["gap_seconds"] == 965

    assert data[1]["developer_id"] == "developer_02"
    assert data[1]["previous_source"] == "github"
    assert data[1]["current_source"] == "slack"
    assert data[1]["gap_seconds"] == 600


def test_context_switches_endpoint_returns_empty_list():
    with patch(
        "backend.app.api.analytics.get_context_switches",
        return_value=[],
    ):
        response = client.get("/api/v1/context-switches")

    assert response.status_code == 200
    assert response.json() == []

def test_developer_transition_summary_endpoint():
    mock_data = [
        {
            "developer_id": "developer_01",
            "team_id": "team_01",
            "total_transitions": 27,
            "short_gap_transitions": 14,
            "long_gap_transitions": 13,
            "avg_gap_seconds": 2744.4,
            "min_gap_seconds": 126,
            "max_gap_seconds": 18954,
        },
        {
            "developer_id": "developer_05",
            "team_id": "team_02",
            "total_transitions": 22,
            "short_gap_transitions": 11,
            "long_gap_transitions": 11,
            "avg_gap_seconds": 2900.7,
            "min_gap_seconds": 30,
            "max_gap_seconds": 10319,
        },
    ]

    with patch(
        "backend.app.api.analytics.get_developer_transition_summary",
        return_value=mock_data,
    ):
        response = client.get(
            "/api/v1/developers/transitions/summary"
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert data[0]["developer_id"] == "developer_01"
    assert data[0]["total_transitions"] == 27
    assert data[0]["short_gap_transitions"] == 14
    assert data[0]["long_gap_transitions"] == 13

    assert data[1]["developer_id"] == "developer_05"
    assert data[1]["total_transitions"] == 22


def test_developer_transition_summary_endpoint_returns_empty_list():
    with patch(
        "backend.app.api.analytics.get_developer_transition_summary",
        return_value=[],
    ):
        response = client.get(
            "/api/v1/developers/transitions/summary"
        )

    assert response.status_code == 200
    assert response.json() == []

def test_transition_summary_endpoint():
    mock_data = [
        {
            "team_id": "team_01",
            "previous_source": "github",
            "current_source": "slack",
            "total_transitions": 12,
            "short_gap_transitions": 5,
            "long_gap_transitions": 7,
            "avg_gap_seconds": 3200.5,
            "min_gap_seconds": 120,
            "max_gap_seconds": 9000,
        },
        {
            "team_id": "team_02",
            "previous_source": "ide",
            "current_source": "jira",
            "total_transitions": 8,
            "short_gap_transitions": 4,
            "long_gap_transitions": 4,
            "avg_gap_seconds": 2500.0,
            "min_gap_seconds": 300,
            "max_gap_seconds": 6000,
        },
    ]

    with patch(
        "backend.app.api.analytics.get_transition_summary",
        return_value=mock_data,
    ):
        response = client.get("/api/v1/transitions/summary")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["team_id"] == "team_01"
    assert data[0]["total_transitions"] == 12
    assert data[0]["short_gap_transitions"] == 5
    assert data[0]["long_gap_transitions"] == 7
    assert data[1]["team_id"] == "team_02"
    assert data[1]["total_transitions"] == 8


def test_transition_summary_endpoint_returns_empty_list():
    with patch(
        "backend.app.api.analytics.get_transition_summary",
        return_value=[],
    ):
        response = client.get("/api/v1/transitions/summary")

    assert response.status_code == 200
    assert response.json() == []
