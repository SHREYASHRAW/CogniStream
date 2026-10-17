import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(45)

OUTPUT_FILE = Path("data/raw/ide_events.jsonl")

DEVELOPER_TEAMS = {
    "developer_01": "team_01",
    "developer_02": "team_01",
    "developer_03": "team_01",
    "developer_04": "team_02",
    "developer_05": "team_02",
}

EVENT_TEMPLATES = [
    {
        "event_type": "coding_session",
        "metadata": {
            "editor": "vscode",
            "language": "python",
            "duration_min": 45,
            "project": "cognistream",
        },
    },
    {
        "event_type": "file_edit",
        "metadata": {
            "editor": "vscode",
            "language": "python",
            "file_extension": ".py",
            "project": "cognistream",
        },
    },
    {
        "event_type": "debugging_session",
        "metadata": {
            "editor": "vscode",
            "language": "python",
            "duration_min": 20,
            "project": "cognistream",
        },
    },
    {
        "event_type": "test_run",
        "metadata": {
            "editor": "vscode",
            "test_framework": "pytest",
            "result": "passed",
            "project": "cognistream",
        },
    },
    {
        "event_type": "terminal_command",
        "metadata": {
            "editor": "vscode",
            "command_category": "git",
            "project": "cognistream",
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
            "event_id": f"ide_mock_{i:03d}",
            "source": "ide",
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

    print(f"Generated {len(events)} synthetic IDE events.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Unique developers: {len({event['developer_id'] for event in events})}")
    print("Source check:", all(event["source"] == "ide" for event in events))
    print("Required-field check:", all(
        all(field in event for field in [
            "event_id", "source", "event_type", "developer_id",
            "team_id", "timestamp", "metadata"
        ])
        for event in events
    ))

if __name__ == "__main__":
    main()
