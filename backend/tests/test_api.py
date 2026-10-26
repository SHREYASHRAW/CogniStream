
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
