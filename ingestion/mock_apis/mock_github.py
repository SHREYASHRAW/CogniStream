import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(42)

OUTPUT_FILE = Path("data/raw/github_events.jsonl")

DEVELOPER_TEAMS = {
    "developer_01": "team_01",
    "developer_02": "team_01",
    "developer_03": "team_01",
    "developer_04": "team_02",
    "developer_05": "team_02",
}

EVENT_TEMPLATES = [
    {
        "event_type": "push",
        "metadata": {"repository": "cognistream-api", "commits": 3, "branch": "feature/metrics"},
    },
    {
        "event_type": "pull_request_opened",
        "metadata": {"repository": "cognistream-api", "pull_request_id": 104, "base_branch": "main"},
    },
    {
        "event_type": "pull_request_reviewed",
        "metadata": {"repository": "cognistream-frontend", "pull_request_id": 98, "review_state": "approved"},
    },
    {
        "event_type": "issue_opened",
        "metadata": {"repository": "cognistream-api", "issue_id": 52, "priority": "medium"},
    },
    {
        "event_type": "commit",
        "metadata": {"repository": "cognistream-data", "branch": "main", "files_changed": 4},
    },
]

def generate_events(count=30):
    now = datetime.now(timezone.utc)
    events = []

    for i in range(1, count + 1):
        template = random.choice(EVENT_TEMPLATES)
        event_time = now - timedelta(minutes=random.randint(1, 1440))

        events.append({
            "event_id": f"gh_mock_{i:03d}",
            "source": "github",
            "event_type": template["event_type"],
            "developer_id": (developer_id := f"developer_{random.randint(1, 5):02d}"),
            "team_id": DEVELOPER_TEAMS[developer_id],
            "timestamp": event_time.isoformat(),
            "metadata": template["metadata"].copy(),
        })

    events.sort(key=lambda event: event["timestamp"])
    return events

def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    events = generate_events()

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    print(f"Generated {len(events)} synthetic GitHub events.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Unique developers: {len({event['developer_id'] for event in events})}")
    print("Source check:", all(event["source"] == "github" for event in events))
    print("Required-field check:", all(
        all(field in event for field in [
            "event_id", "source", "event_type", "developer_id",
            "team_id", "timestamp", "metadata"
        ])
        for event in events
    ))

if __name__ == "__main__":
    main()
