
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
            SELECT source, count() AS event_count
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
