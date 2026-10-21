
-- CogniStream: Validate developer-level event gap classification.
-- Short gaps are <= 1800 seconds; long gaps are > 1800 seconds.
-- These are event activity patterns, not direct measures of productivity
-- or cognitive load.

WITH numbered_events AS
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

event_gaps AS
(
    SELECT
        developer_id,
        team_id,
        source,
        previous_source,
        dateDiff('second', previous_timestamp, timestamp) AS gap_seconds
    FROM numbered_events
    WHERE event_number > 1
),

developer_validation AS
(
    SELECT
        developer_id,
        team_id,
        count() AS total_gaps,

        countIf(gap_seconds <= 1800) AS short_gaps,
        countIf(gap_seconds > 1800) AS long_gaps,

        countIf(
            gap_seconds > 1800
            AND source != previous_source
        ) AS long_gaps_with_source_change,

        countIf(
            gap_seconds > 1800
            AND source = previous_source
        ) AS long_gaps_same_source

    FROM event_gaps
    GROUP BY developer_id, team_id
)

SELECT
    developer_id,
    team_id,
    total_gaps,
    short_gaps,
    long_gaps,
    long_gaps_with_source_change,
    long_gaps_same_source,

    long_gaps
        - long_gaps_with_source_change
        - long_gaps_same_source AS unclassified_long_gaps,

    total_gaps
        - short_gaps
        - long_gaps AS unclassified_gaps

FROM developer_validation
ORDER BY developer_id;
