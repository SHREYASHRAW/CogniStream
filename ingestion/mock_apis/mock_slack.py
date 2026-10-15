import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

random.seed(43)

OUTPUT_FILE = Path("data/raw/slack_events.jsonl")

EVENT_TEMPLATES = [
    {
        "event_type": "message",
        "metadata": {
            "channel": "engineering",
            "message_category": "project_update",
            "message_length": 120,
        },
    },
    {
        "event_type": "thread_reply",
        "metadata": {
            "channel": "engineering",
            "message_category": "technical_discussion",
            "message_length": 85,
        },
    },
    {
        "event_type": "reaction_added",
        "metadata": {
            "channel": "team-updates",
            "reaction": "thumbsup",
        },
    },
    {
        "event_type": "message",
        "metadata": {
            "channel": "team-updates",
            "message_category": "status_update",
            "message_length": 65,
        },
    },
    {
        "event_type": "thread_reply",
        "metadata": {
            "channel": "help-engineering",
            "message_category": "question",
            "message_length": 95,
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
            "event_id": f"slack_mock_{i:03d}",
            "source": "slack",
            "event_type": template["event_type"],
            "developer_id": f"developer_{random.randint(1, 5):02d}",
            "team_id": f"team_{random.randint(1, 2):02d}",
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

    print(f"Generated {len(events)} synthetic Slack events.")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Unique developers: {len({event['developer_id'] for event in events})}")
    print("Source check:", all(event["source"] == "slack" for event in events))
    print("Required-field check:", all(
        all(field in event for field in [
            "event_id", "source", "event_type", "developer_id",
            "team_id", "timestamp", "metadata"
        ])
        for event in events
    ))

if __name__ == "__main__":
    main()
