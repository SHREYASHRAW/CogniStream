
-- CogniStream: Team-level event gap analysis.
-- A long gap is defined as more than 30 minutes between
-- consecutive events for the same developer and team.
-- Event gaps do not directly measure cognitive load,
-- interruption cost, or developer productivity.

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
        team_id,
        developer_id,
        source,
        previous_source,
        dateDiff('second', previous_timestamp, timestamp)
            AS gap_seconds
    FROM numbered_events
    WHERE event_number > 1
)

SELECT
    team_id,
    count() AS consecutive_gaps,

    countIf(gap_seconds > 1800) AS long_gaps,

    round(
        100.0 * countIf(gap_seconds > 1800) / count(),
        1
    ) AS long_gap_percentage,

    countIf(
        gap_seconds > 1800
        AND source != previous_source
    ) AS long_gaps_with_source_change

FROM event_gaps

GROUP BY team_id
ORDER BY team_id;
