
-- CogniStream: Validate event data quality in ClickHouse.
-- Read-only checks; this query does not modify stored data.
-- Expected source and event-type values reflect the current
-- synthetic dataset and should be updated if the schema evolves.

-- 1. Total number of stored events
SELECT
    'total_rows' AS check_name,
    count() AS issue_count
FROM developer_events

UNION ALL

-- 2. Count event IDs that appear more than once
SELECT
    'duplicate_event_id_rows' AS check_name,
    count() AS issue_count
FROM
(
    SELECT event_id
    FROM developer_events
    GROUP BY event_id
    HAVING count() > 1
)

UNION ALL

-- 3. Count rows with one or more required fields missing
SELECT
    'missing_required_fields' AS check_name,
    countIf(
        event_id = ''
        OR developer_id = ''
        OR team_id = ''
        OR source = ''
        OR event_type = ''
        OR metadata_json = ''
    ) AS issue_count
FROM developer_events

UNION ALL

-- 4. Check for unexpected source values
SELECT
    'unexpected_source_values' AS check_name,
    countIf(source NOT IN ('github', 'ide', 'jira', 'slack')) AS issue_count
FROM developer_events

UNION ALL

-- 5. Check for unexpected event types
SELECT
    'unexpected_event_type_values' AS check_name,
    countIf(
        event_type NOT IN
        (
            'coding_session',
            'commit',
            'debugging_session',
            'file_edit',
            'issue_assigned',
            'issue_completed',
            'issue_created',
            'issue_opened',
            'issue_status_changed',
            'message',
            'pull_request_opened',
            'pull_request_reviewed',
            'push',
            'reaction_added',
            'terminal_command',
            'test_run',
            'thread_reply'
        )
    ) AS issue_count
FROM developer_events

UNION ALL

-- 6. Check for missing event IDs
SELECT
    'missing_event_id' AS check_name,
    countIf(event_id = '') AS issue_count
FROM developer_events

UNION ALL

-- 7. Check for missing developer IDs
SELECT
    'missing_developer_id' AS check_name,
    countIf(developer_id = '') AS issue_count
FROM developer_events

UNION ALL

-- 8. Check for missing team IDs
SELECT
    'missing_team_id' AS check_name,
    countIf(team_id = '') AS issue_count
FROM developer_events

UNION ALL

-- 9. Check for missing source values
SELECT
    'missing_source' AS check_name,
    countIf(source = '') AS issue_count
FROM developer_events

UNION ALL

-- 10. Check for missing event types
SELECT
    'missing_event_type' AS check_name,
    countIf(event_type = '') AS issue_count
FROM developer_events

UNION ALL

-- 11. Check for missing metadata JSON
SELECT
    'missing_metadata_json' AS check_name,
    countIf(metadata_json = '') AS issue_count
FROM developer_events

UNION ALL

-- 12. Check for malformed JSON in metadata_json
SELECT
    'invalid_metadata_json' AS check_name,
    countIf(NOT isValidJSON(metadata_json)) AS issue_count
FROM developer_events


UNION ALL

-- Flag timestamps outside the current synthetic dataset window.
-- Update this window when the dataset's expected dates change.
SELECT
    'invalid_timestamp_window' AS check_name,
    countIf(
        timestamp < toDateTime64('2026-10-16 00:00:00', 3, 'UTC')
        OR timestamp >= toDateTime64('2026-10-18 00:00:00', 3, 'UTC')
    ) AS issue_count
FROM developer_events

UNION ALL

-- Each developer should belong to exactly one team.
SELECT
    'inconsistent_developer_team' AS check_name,
    count() AS issue_count
FROM
(
    SELECT developer_id
    FROM developer_events
    GROUP BY developer_id
    HAVING countDistinct(team_id) > 1
)

ORDER BY check_name;
