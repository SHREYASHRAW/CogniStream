# CogniStream — Developer Flow-State & Cognitive Load Analytics

**CogniStream** is a data analytics and engineering project designed to analyze developer activity patterns, identify potential interruptions to focused work, and help engineering teams understand workflow friction.

Rather than measuring productivity solely through commits or tickets, CogniStream combines timestamped activity events from development tools to investigate uninterrupted work sessions and interruption patterns.

> **Project status:** In development  
> **Organization:** Infotact Solutions

## Objectives

- Ingest developer activity events from mock GitHub, Slack, Jira, and IDE activity APIs.
- Orchestrate scheduled extraction workflows using Apache Airflow.
- Clean and transform event data using Python and Polars.
- Store and analyze timestamped events in ClickHouse.
- Identify uninterrupted flow sessions using explicit, configurable rules.
- Analyze interruption frequency, timing, and potential context-switching costs.
- Present analytical findings through a custom React and Tremor.js dashboard.
- Expose aggregated analytics through FastAPI.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Data ingestion and analytics |
| Apache Airflow | Workflow orchestration |
| Polars | Data transformation |
| ClickHouse | Analytical event storage |
| SQL | Analytical queries and aggregations |
| FastAPI | Backend API |
| React | Frontend application |
| Tremor.js | Dashboard components |
| Git and GitHub | Version control |

## Proposed Architecture

1. **Data sources:** Mock GitHub, Slack, Jira, and IDE activity events.
2. **Ingestion:** Python extraction scripts collect and validate event payloads.
3. **Orchestration:** Airflow schedules and monitors ingestion workflows.
4. **Processing:** Polars normalizes and transforms timestamped events.
5. **Storage:** ClickHouse stores unified event records.
6. **Analytics:** SQL and Python calculate flow-session and interruption metrics.
7. **API:** FastAPI serves aggregated analytical results.
8. **Dashboard:** React and Tremor.js present interactive visualizations.

## Planned Analytics

- Uninterrupted flow-session duration and frequency.
- Potential interruption counts by source and time.
- IDE activity and notification timelines.
- Team-level workflow patterns.
- Estimated context-switching and recovery costs.
- Before-and-after comparisons for hypothetical notification-policy changes.

Flow-state indicators will be treated as analytical proxies, not direct measurements of mental state. Estimated recovery costs will be documented separately from observed events.

## Development Roadmap

| Phase | Planned deliverables |
|---|---|
| Week 1 | Mock API extraction, Airflow setup, and React dashboard scaffolding |
| Week 2 | ClickHouse schema, Polars transformations, and baseline metrics |
| Week 3 | Flow-session logic, interruption analysis, and friction visualizations |
| Week 4 | FastAPI integration, dashboard refinement, testing, and documentation |

## Repository Structure

```text
CogniStream/
├── airflow/
│   └── dags/
├── ingestion/
│   ├── extractors/
│   ├── mock_apis/
│   └── schemas/
├── processing/
├── sql/
│   ├── schemas/
│   └── analytics/
├── data/
│   ├── raw/
│   └── processed/
├── backend/
│   └── app/
├── frontend/
├── tests/
├── docs/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Data and Privacy

The initial implementation will use synthetic developer activity data. Real developer activity can be sensitive, so future integrations should follow appropriate access controls, data minimization, and aggregation practices.

Generated datasets, credentials, and local environment files should not be committed to the repository.

## Project Status

The repository structure and initial configuration are being prepared. Ingestion pipelines, analytical models, infrastructure, and dashboard components will be implemented incrementally and validated throughout development.