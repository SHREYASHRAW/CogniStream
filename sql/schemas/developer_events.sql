CREATE TABLE IF NOT EXISTS developer_events
(
    event_id String,
    source LowCardinality(String),
    event_type LowCardinality(String),
    developer_id String,
    team_id String,
    timestamp DateTime64(3, 'UTC'),
    metadata_json String
)
ENGINE = MergeTree
ORDER BY (team_id, developer_id, timestamp, event_id);
