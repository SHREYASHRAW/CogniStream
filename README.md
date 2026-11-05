# CogniStream

## Developer Flow-State & Cognitive Load Analytics

CogniStream is a data engineering and analytics portfolio project that
explores developer workflows, cross-platform activity, and potential
context switching.

It unifies **synthetic** activity events from GitHub, Slack, Jira, and
IDE activity into an analytical dataset. Event sequences, source
transitions, and time gaps are used as descriptive workflow
indicators---not as direct measurements of cognitive load or
productivity.

> **Current status:** Synthetic event generation, schema validation,
> Python/Polars processing, ClickHouse storage, SQL analytics, Apache
> Airflow orchestration, a FastAPI analytics endpoint, and automated
> tests are implemented. The React + Tremor.js dashboard and further
> advanced analytics remain in progress.

## Table of Contents

-   [Problem Statement](#problem-statement)
-   [Project Objectives](#project-objectives)
-   [Architecture](#architecture)
-   [Technology Stack](#technology-stack)
-   [Current Implementation](#current-implementation)
-   [API Reference](#api-reference)
-   [Analytics Methodology](#analytics-methodology)
-   [Data Quality and Testing](#data-quality-and-testing)
-   [Repository Structure](#repository-structure)
-   [Getting Started](#getting-started)
-   [Current Limitations](#current-limitations)
-   [Roadmap](#roadmap)

------------------------------------------------------------------------

## Problem Statement

Software engineering work often spans multiple tools. A developer may
switch between code changes, messages, issue updates, and local IDE
activity throughout a work session. These activities are distributed
across systems, making it difficult to understand the sequence of work
and identify patterns of cross-tool activity.

CogniStream explores questions such as:

-   How is activity distributed across developer tools?
-   How frequently do recorded events transition between sources?
-   How do event-to-event time gaps vary across teams and source
    transitions?
-   How could these indicators support a developer workflow analytics
    dashboard?

A source transition is not necessarily an interruption, and a time gap
does not prove lost productivity.

## Project Objectives

1.  Generate representative synthetic developer activity events from
    multiple sources.
2.  Validate events against a shared schema.
3.  Consolidate events into a unified dataset using Python and Polars.
4.  Store events in ClickHouse for analytical queries.
5.  Analyze activity distribution, source transitions, and event gaps.
6.  Orchestrate validation, processing, loading, and verification with
    Apache Airflow.
7.  Expose summary analytics through a FastAPI backend.
8.  Test processing and API behavior automatically.
9.  Build an interactive React + Tremor.js dashboard.

## Architecture

### Implemented data pipeline

``` text
Synthetic Event Sources
  ├── GitHub
  ├── Slack
  ├── Jira
  └── IDE Activity
          |
          v
     JSONL Event Files
          |
          v
     Schema Validation
          |
          v
  Python + Polars Processing
          |
          v
 Unified Parquet Dataset
          |
          v
       ClickHouse
          ^
          |
 Apache Airflow DAG
 (validate → process → load → verify)
          |
          v
      FastAPI Backend
          |
          v
  GET /api/v1/summary
```

### Planned frontend

``` text
React + Tremor.js Dashboard
             |
             v
       FastAPI Backend
             |
             v
          ClickHouse
```

The backend currently provides a summary endpoint. The full dashboard
and additional dashboard-oriented analytics are not yet complete.

## Technology Stack

  -----------------------------------------------------------------------
  Technology              Purpose                 Status
  ----------------------- ----------------------- -----------------------
  Python                  Event validation,       Implemented
                          processing, backend
                          logic

  JSON / JSONL            Synthetic event records Implemented

  Polars                  Data transformation and Implemented
                          Parquet generation

  Parquet                 Processed event storage Implemented

  ClickHouse              Analytical event        Implemented
                          storage and SQL queries

  SQL                     Activity summaries and  Implemented
                          source-transition
                          analysis

  Apache Airflow          Pipeline orchestration  Implemented and tested

  FastAPI                 HTTP API for summary    Implemented
                          analytics

  Uvicorn                 Local ASGI server       Used for local
                                                  development

  pytest                  Automated testing       Implemented

  React + Tremor.js       Interactive analytics   Planned / in progress
                          dashboard

  Git and GitHub          Version control and     Used
                          documentation
  -----------------------------------------------------------------------

## Current Implementation

### 1. Synthetic event generation

Four sources simulate developer activity:

-   GitHub
-   Slack
-   Jira
-   IDE activity

The current synthetic dataset contains **120 events**, with **30 events
per source**.

### 2. Event schema validation

A JSON schema and Python validation script check event records before
processing. The latest recorded validation checkpoint reported **120
valid events out of 120**, with zero validation errors.

Run validation from the repository root:

``` powershell
python ingestion/schemas/validate_events.py
```

### 3. Data processing

The Python processing pipeline reads the four JSONL files,
validates/parses records, normalizes event fields, serializes metadata,
converts timestamps to UTC-aware datetimes, sorts events
chronologically, and writes the consolidated Parquet dataset.

``` powershell
python processing/combine_events.py
```

Output:

``` text
data/processed/all_events.parquet
```

### 4. ClickHouse storage

The unified dataset is stored in the `developer_events` table in the
`cognistream` database. The last verified checkpoint contained **120
rows and 120 unique event IDs**.

The table includes event identifiers, source, event type, developer and
team identifiers, timestamps, and JSON metadata.

### 5. SQL analytics

Existing SQL analytics explore:

-   Source activity summaries.
-   Source transitions grouped by team and source pair.
-   Potential source changes for individual developers.
-   Team-level event-gap summaries.
-   Validation of event-gap classifications.

These are descriptive indicators for exploratory analysis; they do not
directly measure cognitive load or productivity.

### 6. Apache Airflow orchestration

The CogniStream Airflow DAG orchestrates four pipeline tasks:

1.  `validate_raw_events`
2.  `combine_events_to_parquet`
3.  `load_events_to_clickhouse`
4.  `verify_clickhouse_load`

A successful run has been verified with all four tasks succeeding and
the 120-event dataset present in ClickHouse.

The current Airflow setup is for local development and should not be
treated as a production deployment.

### 7. FastAPI analytics backend

The FastAPI application connects to ClickHouse through centralized
environment-based configuration. Its summary service queries event,
developer, and team counts and groups events by source.

Available endpoints:

-   `GET /` --- basic API information.
-   `GET /health` --- API health response.
-   `GET /api/v1/summary` --- summary statistics from ClickHouse.

Example summary response:

``` json
{
  "total_events": 120,
  "unique_developers": 5,
  "unique_teams": 2,
  "events_by_source": [
    {"source": "github", "count": 30},
    {"source": "ide", "count": 30},
    {"source": "jira", "count": 30},
    {"source": "slack", "count": 30}
  ]
}
```

Counts are based on the current synthetic dataset and may change when
the input data changes.

## API Reference

  -----------------------------------------------------------------------
  Method                  Endpoint                Purpose
  ----------------------- ----------------------- -----------------------
  `GET`                   `/`                     Basic API information

  `GET`                   `/health`               Health check

  `GET`                   `/api/v1/summary`       Event, developer, team,
                                                  and source counts
  -----------------------------------------------------------------------

When the local API is running, interactive API documentation is
available at:

``` text
http://127.0.0.1:8000/docs
```

## Analytics Methodology

### Source transitions

A transition occurs when two consecutive recorded events for the same
developer have different source values. Transitions can be grouped by
team and source pair.

### Event-gap classification

The current SQL analysis uses a threshold of **1,800 seconds (30
minutes)** to distinguish shorter from longer event gaps. This is an
exploratory assumption, not a validated cognitive-science threshold.

### Interpretation limits

-   A source transition does not prove an interruption occurred.
-   A gap between events does not establish how long focus recovery
    took.
-   Synthetic events do not represent observed employee behavior.
-   Event counts are not equivalent to productivity or work quality.
-   Team and developer summaries describe the generated dataset, not
    actual employee performance.

## Data Quality and Testing

The project includes schema validation, ClickHouse data-quality queries,
processing tests, and API tests.

Run the complete test suite from the repository root:

``` powershell
python -m pytest -v
```

**Latest recorded test result:** 22 tests passed. Re-run the suite after
changes to confirm the current result.

The API tests cover the root endpoint, health endpoint, and analytics
summary response. The summary test uses the current local ClickHouse
dataset, so ClickHouse must be available and populated when running the
complete API test suite.

## Repository Structure

``` text
CogniStream/
├── airflow/
│   └── dags/
│       └── cognistream_pipeline.py
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── analytics.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── services/
│   │   │   ├── analytics.py
│   │   │   └── clickhouse.py
│   │   └── main.py
│   └── tests/
│       └── test_api.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── frontend/
├── ingestion/
│   ├── mock_apis/
│   └── schemas/
├── processing/
│   └── combine_events.py
├── sql/
│   ├── analytics/
│   └── schemas/
├── tests/
├── requirements.txt
└── README.md
```

Some directories are intended for future work and may not yet contain a
complete implementation.

## Getting Started

### Prerequisites

-   Python and the project's dependencies installed in a virtual
    environment.
-   Git.
-   A running ClickHouse instance.
-   The local `.env` file configured with the ClickHouse connection
    settings.

### 1. Clone the repository

``` powershell
git clone https://github.com/SHREYASHRAW/CogniStream.git
cd CogniStream
```

### 2. Create and activate a virtual environment

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

``` powershell
python -m pip install -r requirements.txt
```

### 4. Configure ClickHouse

Create a local `.env` file at the repository root and configure the
connection values used by the backend:

``` dotenv
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=cognistream
CLICKHOUSE_USER=cogni
CLICKHOUSE_PASSWORD=your_local_password
```

Replace the example password with your local ClickHouse password. **Do
not commit `.env` or real credentials to Git.** The backend loads these
settings from environment variables and the root `.env` file.

### 5. Generate and process events

Generate or prepare the synthetic source files under `data/raw/`,
validate them, and run:

``` powershell
python ingestion/schemas/validate_events.py
python processing/combine_events.py
```

### 6. Start the API

From the repository root, with the virtual environment active and
ClickHouse available:

``` powershell
python -m uvicorn backend.app.main:app --reload
```

Open these local URLs:

-   API root: `http://127.0.0.1:8000/`
-   Health check: `http://127.0.0.1:8000/health`
-   Analytics summary: `http://127.0.0.1:8000/api/v1/summary`
-   Interactive docs: `http://127.0.0.1:8000/docs`

### 7. Run tests

``` powershell
python -m pytest -v
```

The API summary test queries ClickHouse, so ensure the database contains
the expected test dataset before running the full suite.

### 8. Run the Airflow pipeline

Use the project's local Docker Compose/Airflow setup and ensure
ClickHouse is running and reachable from the Airflow container. The DAG
validates raw events, creates the Parquet dataset, loads new events into
ClickHouse, and verifies the load.

Connection values should be supplied through local environment
configuration. Do not commit passwords, tokens, or other secrets.

## Current Limitations

-   Data is synthetic and generated for development and testing.
-   Ingestion uses local files rather than live external APIs.
-   The dataset is small and intended for functional validation.
-   Workflow indicators have not been validated against real developer
    workflows.
-   The current API exposes a summary endpoint; more analytical
    endpoints are still needed.
-   The React + Tremor.js dashboard is not yet complete.
-   No claims of measured cognitive load, focus recovery, or
    productivity improvement are made.

## Roadmap

-   [x] Create synthetic GitHub, Slack, Jira, and IDE event generators.
-   [x] Implement schema validation.
-   [x] Consolidate events using Python and Polars.
-   [x] Store unified events in ClickHouse.
-   [x] Create baseline source activity and transition analytics.
-   [x] Add automated processing and data-quality tests.
-   [x] Orchestrate validation, processing, loading, and verification
    with Apache Airflow.
-   [x] Expose summary analytics through FastAPI.
-   [x] Add automated API tests.
-   [ ] Expand analytics endpoints and analytical edge-case tests.
-   [ ] Refine session definitions and event-gap interpretation.
-   [ ] Build the React + Tremor.js dashboard.
-   [ ] Add dashboard integration and end-to-end tests.
-   [ ] Complete reproducible end-to-end setup documentation.

## Project Philosophy

CogniStream is a learning and portfolio project focused on practical
data engineering, analytical SQL, testing, and transparent
interpretation of data.

The guiding principle is to measure what the data supports, document
assumptions clearly, and avoid presenting workflow proxies as direct
measures of human cognition.
