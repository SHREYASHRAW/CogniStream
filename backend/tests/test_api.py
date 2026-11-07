
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
