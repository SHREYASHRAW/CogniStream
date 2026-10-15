import json
from datetime import datetime
from pathlib import Path

SCHEMA_PATH = Path("ingestion/schemas/event_schema.json")

EVENT_FILES = {
    "github": Path("data/raw/github_events.jsonl"),
    "slack": Path("data/raw/slack_events.jsonl"),
    "jira": Path("data/raw/jira_events.jsonl"),
    "ide": Path("data/raw/ide_events.jsonl"),
}

with SCHEMA_PATH.open("r", encoding="utf-8-sig") as file:
    schema = json.load(file)

required_fields = set(schema["required"])
allowed_fields = set(schema["properties"])
allowed_sources = set(schema["properties"]["source"]["enum"])

errors = []
total_events = 0
total_valid = 0
seen_ids = set()

for expected_source, file_path in EVENT_FILES.items():
    if not file_path.exists():
        errors.append(f"{file_path}: File not found.")
        print(f"{expected_source.title()}: FILE MISSING")
        continue

    file_total = 0
    file_valid = 0

    with file_path.open("r", encoding="utf-8-sig") as file:
        for line_number, line in enumerate(file, start=1):
            if not line.strip():
                continue

            total_events += 1
            file_total += 1
            event_errors = []

            try:
                event = json.loads(line)
            except json.JSONDecodeError as error:
                errors.append(
                    f"{file_path}, line {line_number}: Invalid JSON ({error})."
                )
                continue

            if not isinstance(event, dict):
                errors.append(
                    f"{file_path}, line {line_number}: Event must be an object."
                )
                continue

            missing = required_fields - set(event)
            extra = set(event) - allowed_fields

            if missing:
                event_errors.append(f"Missing fields: {sorted(missing)}")

            if extra:
                event_errors.append(f"Unexpected fields: {sorted(extra)}")

            if event.get("source") not in allowed_sources:
                event_errors.append("Unsupported source.")
            elif event.get("source") != expected_source:
                event_errors.append(
                    f"Expected source '{expected_source}', "
                    f"got '{event.get('source')}'."
                )

            for field in (
                "event_id", "event_type", "developer_id", "team_id"
            ):
                value = event.get(field)
                if not isinstance(value, str) or not value.strip():
                    event_errors.append(
                        f"'{field}' must be a non-empty string."
                    )

            if not isinstance(event.get("metadata"), dict):
                event_errors.append("'metadata' must be an object.")

            timestamp = event.get("timestamp")
            if not isinstance(timestamp, str):
                event_errors.append("'timestamp' must be a string.")
            else:
                try:
                    parsed = datetime.fromisoformat(
                        timestamp.replace("Z", "+00:00")
                    )
                    if parsed.tzinfo is None:
                        event_errors.append(
                            "Timestamp must include a timezone."
                        )
                except ValueError:
                    event_errors.append("Invalid timestamp format.")

            event_id = event.get("event_id")
            if isinstance(event_id, str) and event_id:
                if event_id in seen_ids:
                    event_errors.append(f"Duplicate event_id: {event_id}")
                else:
                    seen_ids.add(event_id)

            if event_errors:
                for message in event_errors:
                    errors.append(
                        f"{file_path}, line {line_number}: {message}"
                    )
            else:
                file_valid += 1
                total_valid += 1

    print(
        f"{expected_source.title()}: "
        f"{file_valid}/{file_total} valid events"
    )

print(f"Total events: {total_events}")
print(f"Valid events: {total_valid}")
print(f"Validation errors: {len(errors)}")

if errors:
    for error in errors:
        print("-", error)
    print("Schema validation: FAILED")
    raise SystemExit(1)

print("Schema validation: PASSED")
