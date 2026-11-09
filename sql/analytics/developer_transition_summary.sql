-- CogniStream: Developer-level source transition analysis.
-- Event gaps are workflow timing proxies, not measures of
-- cognitive recovery or proven interruption cost.

WITH settings AS
(
    SELECT 1800 AS gap_threshold_seconds
),

numbered_events AS
(
    SELECT
        event_id,
        developer_id,
        team_id,
        source,
        timestamp,

        row_number() OVER
        (
            PARTITION BY developer_id, team_id
            ORDER BY timestamp, event_id
        ) AS event_number,

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

    FROM cognistream.developer_events
),

transitions AS
(
    SELECT
        developer_id,
        team_id,
        dateDiff('second', previous_timestamp, timestamp) AS gap_seconds

    FROM numbered_events

    WHERE event_number > 1
      AND previous_source != source
)

SELECT
    developer_id,
    team_id,
    count() AS total_transitions,

    countIf(
        gap_seconds <=
        (SELECT gap_threshold_seconds FROM settings)
    ) AS short_gap_transitions,

    countIf(
        gap_seconds >
        (SELECT gap_threshold_seconds FROM settings)
    ) AS long_gap_transitions,

    round(avg(gap_seconds), 1) AS avg_gap_seconds,
    min(gap_seconds) AS min_gap_seconds,
    max(gap_seconds) AS max_gap_seconds

FROM transitions

GROUP BY
    developer_id,
    team_id

ORDER BY
    total_transitions DESC,
    developer_id;