-- CogniStream: Potential context switches between consecutive events.
-- A source change is a workflow proxy, not proof of an interruption.

WITH ordered_events AS
(
    SELECT
        event_id,
        developer_id,
        team_id,
        source,
        event_type,
        timestamp,
        lagInFrame(source, 1, source) OVER
        (
            PARTITION BY developer_id, team_id
            ORDER BY timestamp, event_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS previous_source,
        lagInFrame(timestamp, 1, timestamp) OVER
        (
            PARTITION BY developer_id, team_id
            ORDER BY timestamp, event_id
            ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
        ) AS previous_timestamp
    FROM developer_events
)
SELECT
    developer_id,
    team_id,
    previous_source,
    source AS current_source,
    previous_timestamp,
    timestamp AS current_timestamp,
    dateDiff('second', previous_timestamp, timestamp) AS gap_seconds
FROM ordered_events
WHERE previous_source != source
ORDER BY developer_id, current_timestamp;
