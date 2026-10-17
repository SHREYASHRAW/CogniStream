-- CogniStream: Source-level activity summary
-- These are workflow activity indicators, not direct cognitive measurements.

SELECT
    source,
    count() AS total_events,
    uniqExact(developer_id) AS active_developers,
    min(timestamp) AS first_event,
    max(timestamp) AS last_event
FROM developer_events
GROUP BY source
ORDER BY total_events DESC;
