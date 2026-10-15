import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(44)

OUTPUT_FILE = Path("data/raw/jira_events.jsonl")

EVENT_TEMPLATES = [
    {
        "event_type": "issue_created",
        "metadata": {
            "project": "COG",
            "issue_type": "Task",
            "priority": "Medium",
            "status": "To Do",
        },
    },
    {
        "event_type": "issue_status_changed",
        "metadata": {
            "project": "COG",
            "issue_type": "Bug",
            "from_status": "To Do",
            "to_status": "In Progress",
        },
    },
    {
        "event_type": "issue_status_changed",
        "metadata": {
            "project": "COG",
            "issue_type": "Story",
            "from_status": "In Progress",
            "to_status": "In Review",
        },
    },
    {
        "event_type": "issue_completed",
        "metadata": {
            "project": "COG",
            "issue_type": "Task",
            "status": "Done",
            "resolution": "Completed",
        },
    },
    {
        "event_type": "issue_assigned",
        "metadata": {
            "project": "COG",
            "issue_type": "Bug",
            "priority": "High",
        },
    },
]

def generate_events(count=30):
    now = datetime.now(timezone.utc)
    events = []

    for i in range(1, count + 1):
        template = random.choice(EVENT_TEMPLATES)
        event_time = now - timedelta(minutes=random.randint(1, 1440))

        events.append({
            "event_id": f"jira_mock_{i:03d}",
            "source": "jira",
            "event_type": template["event_type"],
            "developer_id": f"developer_{random.randint(1, 5):02d}",
            "team_id": f"team_{random.randint(1, 2):02d}",
            "timestamp": event_time.isoformat(),
            "metadata": {
                **template["metadata"],
                "issue_key": f"COG-{1000 + i}",
            },
        })

    events.sort(key=lambda event: event["timestamp"])
    return events

def main():
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    events = generate_events()

    with OUTPUT_FILE.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")

    print(f"Generated {len(events)} synthetic Jira events.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Unique developers: {len({event['developer_id'] for event in events})}")
    print("Source check:", all(event["source"] == "jira" for event in events))
    print("Required-field check:", all(
        all(field in event for field in [
            "event_id", "source", "event_type", "developer_id",
            "team_id", "timestamp", "metadata"
        ])
        for event in events
    ))

if __name__ == "__main__":
    main()
