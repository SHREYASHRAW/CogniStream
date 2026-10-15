import json
from datetime import datetime
from pathlib import Path

SCHEMA_PATH = Path("ingestion/schemas/event_schema.json")
EVENTS_PATH = Path("data/raw/github_events.jsonl")

with SCHEMA_PATH.open("r", encoding="utf-8-sig") as file:
    schema = json.load(file)

required_fields = set(schema["required"])
allowed_fields = set(schema["properties"])
allowed_sources = set(schema["properties"]["source"]["enum"])

valid_count = 0
errors = []

with EVENTS_PATH.open("r", encoding="utf-8-sig") as file:
    for line_number, line in enumerate(file, start=1):
        if not line.strip():
            continue

        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            errors.append(f"Line {line_number}: Invalid JSON ({error})")
            continue

        if not isinstance(event, dict):
            errors.append(f"Line {line_number}: Event must be a JSON object.")
            continue

        missing = required_fields - set(event.keys())
        extra = set(event.keys()) - allowed_fields

        if missing:
            errors.append(f"Line {line_number}: Missing fields: {sorted(missing)}")

        if extra:
            errors.append(f"Line {line_number}: Unexpected fields: {sorted(extra)}")

        if event.get("source") not in allowed_sources:
            errors.append(f"Line {line_number}: Unsupported source.")

        for field in ["event_id", "event_type", "developer_id", "team_id"]:
            if not isinstance(event.get(field), str) or not event[field].strip():
                errors.append(f"Line {line_number}: '{field}' must be a non-empty string.")

        if not isinstance(event.get("metadata"), dict):
            errors.append(f"Line {line_number}: 'metadata' must be an object.")

        timestamp = event.get("timestamp")
        if not isinstance(timestamp, str):
            errors.append(f"Line {line_number}: 'timestamp' must be a string.")
        else:
            try:
                parsed_timestamp = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                )
                if parsed_timestamp.tzinfo is None:
                    errors.append(
                        f"Line {line_number}: Timestamp must include a timezone."
                    )
            except ValueError:
                errors.append(f"Line {line_number}: Invalid timestamp format.")

        if not missing and not extra and not any(
            error.startswith(f"Line {line_number}:") for error in errors
        ):
            valid_count += 1

print(f"Events validated: {valid_count}")

if errors:
    print(f"Validation errors: {len(errors)}")
    for error in errors:
        print("-", error)
    raise SystemExit(1)

print("Validation errors: 0")
print("Schema validation: PASSED")
