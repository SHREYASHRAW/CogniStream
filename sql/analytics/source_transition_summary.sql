
-- CogniStream: Team-aware source transition analysis.
-- Event gaps are not direct measures of cognitive recovery
-- time or proven interruption cost.

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

    FROM developer_events
),

transitions AS
(
    SELECT
        team_id,
        developer_id,
        previous_source,
        source AS current_source,
        dateDiff('second', previous_timestamp, timestamp)
            AS gap_seconds
    FROM numbered_events
    WHERE event_number > 1
      AND previous_source != source
)

SELECT
    team_id,
    previous_source,
    current_source,

    count() AS total_transitions,

    countIf(gap_seconds <=
        (SELECT gap_threshold_seconds FROM settings))
        AS short_gap_transitions,

    countIf(gap_seconds >
        (SELECT gap_threshold_seconds FROM settings))
        AS long_gap_transitions,

    round(avg(gap_seconds), 1) AS avg_gap_seconds,
    min(gap_seconds) AS min_gap_seconds,
    max(gap_seconds) AS max_gap_seconds

FROM transitions

GROUP BY
    team_id,
    previous_source,
    current_source

ORDER BY
    team_id,
    total_transitions DESC;
