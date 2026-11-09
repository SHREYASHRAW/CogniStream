from pathlib import Path

from backend.app.services.clickhouse import get_clickhouse_client


def get_summary():
    """Return high-level statistics for ingested developer events."""
    client = get_clickhouse_client()

    try:
        result = client.query(
            """
            SELECT
                count() AS total_events,
                uniqExact(developer_id) AS unique_developers,
                uniqExact(team_id) AS unique_teams
            FROM developer_events
            """
        )

        row = result.first_row

        source_result = client.query(
            """
            SELECT
                source,
                count() AS event_count
            FROM developer_events
            GROUP BY source
            ORDER BY source
            """
        )

        return {
            "total_events": row[0],
            "unique_developers": row[1],
            "unique_teams": row[2],
            "events_by_source": [
                {"source": source, "count": count}
                for source, count in source_result.result_rows
            ],
        }
    finally:
        client.close()


def get_event_trends():
    """Return event counts grouped by hour in UTC."""
    client = get_clickhouse_client()

    try:
        result = client.query(
            """
            SELECT
                toStartOfHour(timestamp) AS hour,
                count() AS event_count
            FROM developer_events
            GROUP BY hour
            ORDER BY hour
            """
        )

        return [
            {
                "timestamp": hour.isoformat(),
                "event_count": count,
            }
            for hour, count in result.result_rows
        ]
    finally:
        client.close()


def get_developer_activity():
    """
    Return event activity grouped by developer, team, and source.

    Developers are ordered by total event count in descending order.
    """
    client = get_clickhouse_client()

    try:
        result = client.query(
            """
            SELECT
                developer_id,
                team_id,
                source,
                count() AS event_count
            FROM developer_events
            GROUP BY
                developer_id,
                team_id,
                source
            ORDER BY
                developer_id,
                source
            """
        )

        developers = {}

        for developer_id, team_id, source, event_count in result.result_rows:
            key = (developer_id, team_id)

            if key not in developers:
                developers[key] = {
                    "developer_id": developer_id,
                    "team_id": team_id,
                    "total_events": 0,
                    "events_by_source": [],
                }

            developers[key]["total_events"] += event_count
            developers[key]["events_by_source"].append(
                {
                    "source": source,
                    "count": event_count,
                }
            )

        return sorted(
            developers.values(),
            key=lambda developer: developer["total_events"],
            reverse=True,
        )

    finally:
        client.close()


def get_source_activity():
    """Return activity statistics grouped by event source."""
    client = get_clickhouse_client()

    try:
        result = client.query(
            """
            SELECT
                source,
                count() AS total_events,
                uniqExact(developer_id) AS active_developers,
                min(timestamp) AS first_event,
                max(timestamp) AS last_event
            FROM developer_events
            GROUP BY source
            ORDER BY total_events DESC
            """
        )

        return [
            {
                "source": source,
                "total_events": total_events,
                "active_developers": active_developers,
                "first_event": first_event.isoformat(),
                "last_event": last_event.isoformat(),
            }
            for (
                source,
                total_events,
                active_developers,
                first_event,
                last_event,
            ) in result.result_rows
        ]

    finally:
        client.close()


def get_context_switches():
    """
    Return potential context switches between consecutive developer events.

    A change in event source is a workflow proxy, not proof of an interruption.
    The SQL logic is maintained in sql/analytics/potential_context_switches.sql.
    """
    client = get_clickhouse_client()

    try:
        project_root = Path(__file__).resolve().parents[3]

        sql_path = (
            project_root
            / "sql"
            / "analytics"
            / "potential_context_switches.sql"
        )

        query = sql_path.read_text(encoding="utf-8")
        result = client.query(query)

        return [
            {
                "developer_id": developer_id,
                "team_id": team_id,
                "previous_source": previous_source,
                "current_source": current_source,
                "previous_timestamp": previous_timestamp.isoformat(),
                "current_timestamp": current_timestamp.isoformat(),
                "gap_seconds": gap_seconds,
            }
            for (
                developer_id,
                team_id,
                previous_source,
                current_source,
                previous_timestamp,
                current_timestamp,
                gap_seconds,
            ) in result.result_rows
        ]

    finally:
        client.close()


def get_transition_summary():
    """
    Return aggregated source-transition statistics by team and source pair.

    Gap classifications describe event timing, not cognitive recovery
    or confirmed interruption costs.

    SQL logic is maintained in sql/analytics/source_transition_summary.sql.
    """
    client = get_clickhouse_client()

    try:
        project_root = Path(__file__).resolve().parents[3]

        sql_path = (
            project_root
            / "sql"
            / "analytics"
            / "source_transition_summary.sql"
        )

        query = sql_path.read_text(encoding="utf-8")
        result = client.query(query)

        return [
            {
                "team_id": team_id,
                "previous_source": previous_source,
                "current_source": current_source,
                "total_transitions": total_transitions,
                "short_gap_transitions": short_gap_transitions,
                "long_gap_transitions": long_gap_transitions,
                "avg_gap_seconds": avg_gap_seconds,
                "min_gap_seconds": min_gap_seconds,
                "max_gap_seconds": max_gap_seconds,
            }
            for (
                team_id,
                previous_source,
                current_source,
                total_transitions,
                short_gap_transitions,
                long_gap_transitions,
                avg_gap_seconds,
                min_gap_seconds,
                max_gap_seconds,
            ) in result.result_rows
        ]

    finally:
        client.close()


def get_developer_transition_summary():
    """
    Return source-transition statistics grouped by developer and team.

    Gap classifications describe event timing, not cognitive recovery
    or confirmed interruption costs.

    SQL logic is maintained in
    sql/analytics/developer_transition_summary.sql.
    """
    client = get_clickhouse_client()

    try:
        project_root = Path(__file__).resolve().parents[3]

        sql_path = (
            project_root
            / "sql"
            / "analytics"
            / "developer_transition_summary.sql"
        )

        query = sql_path.read_text(encoding="utf-8")
        result = client.query(query)

        return [
            {
                "developer_id": developer_id,
                "team_id": team_id,
                "total_transitions": total_transitions,
                "short_gap_transitions": short_gap_transitions,
                "long_gap_transitions": long_gap_transitions,
                "avg_gap_seconds": avg_gap_seconds,
                "min_gap_seconds": min_gap_seconds,
                "max_gap_seconds": max_gap_seconds,
            }
            for (
                developer_id,
                team_id,
                total_transitions,
                short_gap_transitions,
                long_gap_transitions,
                avg_gap_seconds,
                min_gap_seconds,
                max_gap_seconds,
            ) in result.result_rows
        ]

    finally:
        client.close()