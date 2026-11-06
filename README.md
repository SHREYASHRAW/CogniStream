# CogniStream

## Developer Flow-State & Cognitive Load Analytics

CogniStream is a data engineering and analytics portfolio project that explores developer workflows, cross-platform activity, and potential context switching.

It unifies **synthetic activity events** from GitHub, Slack, Jira, and IDE activity into an analytical dataset. Event sequences, source transitions, and time gaps are used as descriptive workflow indicators — not as direct measurements of cognitive load or productivity.

> **Current project status:** Synthetic event generation, schema validation, Python/Polars processing, ClickHouse storage, SQL analytics, Apache Airflow orchestration, a FastAPI analytics endpoint, and automated tests are implemented. The React + Tremor.js dashboard and additional advanced analytics remain in progress.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Problem Statement](#problem-statement)
3. [Project Objectives](#project-objectives)
4. [System Architecture](#system-architecture)
5. [Technology Stack](#technology-stack)
6. [Current Implementation](#current-implementation)
7. [Data Model](#data-model)
8. [Data Pipeline Workflow](#data-pipeline-workflow)
9. [Analytics Methodology](#analytics-methodology)
10. [API Reference](#api-reference)
11. [Project Demonstration Guide](#project-demonstration-guide)
12. [Data Quality and Testing](#data-quality-and-testing)
13. [Repository Structure](#repository-structure)
14. [Getting Started](#getting-started)
15. [Current Limitations](#current-limitations)
16. [Future Roadmap](#future-roadmap)
17. [Project Philosophy](#project-philosophy)

---

## 1. Introduction

Software developers regularly interact with multiple platforms during their work.

These platforms may include:

- GitHub for code changes and repository activity.
- Slack for communication.
- Jira for issue and task management.
- IDE tools for coding activity.

Activity information is distributed across these platforms. CogniStream explores how events from different sources can be collected, standardized, processed, stored, and analyzed in one system.

The project focuses on building a complete data engineering workflow and using its output to explore developer activity patterns.

The current dataset is synthetic and is intended for development, testing, and demonstration.

## 2. Problem Statement

Developer activity is distributed across several tools. A developer may move between coding, reviewing pull requests, checking messages, and updating tasks throughout a work session.

Without a unified view, it can be difficult to understand the sequence and distribution of these activities.

CogniStream explores questions such as:

- How is developer activity distributed across different tools?
- How frequently do recorded events transition between sources?
- How do event-to-event time gaps vary?
- How can activity patterns be represented in an analytics dashboard?
- How can these indicators help explore developer workflow behavior?

A source transition does not necessarily mean an interruption occurred. Similarly, a gap between two events does not prove that productivity or concentration was lost.

## 3. Project Objectives

The main objectives are:

1. Generate representative synthetic developer activity events from multiple sources.
2. Validate events against a common schema.
3. Consolidate events into a unified dataset using Python and Polars.
4. Store processed events in ClickHouse.
5. Analyze activity distribution, source transitions, and event gaps.
6. Orchestrate the data pipeline using Apache Airflow.
7. Expose summary analytics through a FastAPI backend.
8. Test data processing and API behavior automatically.
9. Develop an interactive React + Tremor.js dashboard.

## 4. System Architecture

### 4.1 Overall architecture

The project follows a data engineering pipeline architecture.

```text
                 DATA SOURCES
        ┌──────────┬──────────┬──────────┐
        │ GitHub   │ Slack    │ Jira     │
        └──────────┴──────────┴──────────┘
                         │
                  ┌─────────────┐
                  │ IDE Activity│
                  └─────────────┘
                         │
                         ▼
              SYNTHETIC EVENT DATA
                         │
                         ▼
                SCHEMA VALIDATION
                         │
                         ▼
              PYTHON + POLARS
                  PROCESSING
                         │
                         ▼
               PARQUET DATASET
                         │
                         ▼
                   CLICKHOUSE
                         │
                         ▼
                SQL ANALYTICS
                         │
                         ▼
                  FASTAPI BACKEND
                         │
                         ▼
                ANALYTICS DASHBOARD
                 (PLANNED / IN PROGRESS)

        APACHE AIRFLOW ORCHESTRATES
        THE VALIDATION, PROCESSING,
        LOADING AND VERIFICATION TASKS
```

### 4.2 Implemented data pipeline

The implemented pipeline consists of:

1. Synthetic event generation.
2. Event schema validation.
3. Data consolidation and transformation.
4. Parquet dataset generation.
5. ClickHouse loading.
6. Data load verification.
7. Backend analytics.

### 4.3 Planned frontend architecture

The planned frontend will consume analytics from the FastAPI backend.

```text
       REACT + TREMOR.JS
          DASHBOARD
               │
               ▼
        FASTAPI BACKEND
               │
               ▼
           CLICKHOUSE
```

The current backend provides a summary endpoint. The complete interactive dashboard and additional dashboard-oriented analytics are not yet implemented.

## 5. Technology Stack

| Technology | Purpose | Status |
|---|---|---|
| Python | Event validation, processing and backend development | Implemented |
| JSON / JSONL | Synthetic event records | Implemented |
| Polars | Data transformation and processing | Implemented |
| Parquet | Processed event storage | Implemented |
| ClickHouse | Analytical event storage and querying | Implemented |
| SQL | Activity summaries and source-transition analysis | Implemented |
| Apache Airflow | Pipeline orchestration | Implemented and tested |
| FastAPI | Backend analytics API | Implemented |
| Uvicorn | Local API server | Used for development |
| pytest | Automated testing | Implemented |
| React | Frontend development | Planned / in progress |
| Tremor.js | Dashboard visualizations | Planned / in progress |
| Git and GitHub | Version control | Used |

### Why these technologies?

**Python:** Used as the primary programming language for event validation, transformation, and backend development.

**Polars:** Used for efficient DataFrame operations and processing the event records.

**Parquet:** Provides a columnar format for storing the consolidated dataset efficiently.

**ClickHouse:** Used as the analytical database for storing and querying event data.

**Apache Airflow:** Manages the sequence of pipeline tasks and their dependencies.

**FastAPI:** Exposes backend functionality and analytics through HTTP endpoints.

**React and Tremor.js:** Planned for the interactive dashboard and visualization of analytical results.

## 6. Current Implementation

### 6.1 Synthetic event generation

Four sources simulate developer activity:

- GitHub
- Slack
- Jira
- IDE activity

The current synthetic dataset contains **120 events**, with **30 events per source**.

The dataset represents simulated activity and does not contain real employee behavior.

### 6.2 Event schema validation

A JSON schema and Python validation script check event records before processing.

The latest recorded validation checkpoint reported:

- Total events: 120
- Valid events: 120
- Validation errors: 0

Run validation from the project root:

```powershell
python ingestion/schemas/validate_events.py
```

### 6.3 Data processing

The Python processing pipeline:

- Reads the four JSONL source files.
- Validates and parses the records.
- Normalizes event fields.
- Serializes metadata.
- Converts timestamps into UTC-aware datetimes.
- Sorts events chronologically.
- Generates a consolidated Parquet dataset.

Run the processing script:

```powershell
python processing/combine_events.py
```

Output:

```text
data/processed/all_events.parquet
```

### 6.4 ClickHouse storage

The consolidated dataset is stored in the `developer_events` table inside the `cognistream` database.

The last verified checkpoint contained:

- 120 rows.
- 120 unique event IDs.

The table stores event identifiers, source, event type, developer and team identifiers, timestamps, and JSON metadata.

### 6.5 SQL analytics

Existing SQL analytics explore:

- Activity summaries by source.
- Source transitions grouped by team and source pair.
- Potential source changes for individual developers.
- Team-level event-gap summaries.
- Validation of event-gap classifications.

These are descriptive indicators for exploratory analysis. They do not directly measure cognitive load or productivity.

### 6.6 Apache Airflow orchestration

The CogniStream Airflow DAG orchestrates four pipeline tasks:

1. `validate_raw_events`
2. `combine_events_to_parquet`
3. `load_events_to_clickhouse`
4. `verify_clickhouse_load`

A successful run has been verified with all four tasks succeeding and the 120-event dataset present in ClickHouse.

The current Airflow setup is intended for local development and is not a production deployment.

### 6.7 FastAPI analytics backend

The FastAPI application connects to ClickHouse through centralized environment-based configuration.

The summary service retrieves:

- Total event count.
- Number of unique developers.
- Number of unique teams.
- Event counts grouped by source.

The available endpoints are:

- `GET /` — Basic API information.
- `GET /health` — API health response.
- `GET /api/v1/summary` — Summary statistics from ClickHouse.

Example summary response:

```json
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

The values above represent the current synthetic dataset and may change when the input data changes.

## 7. Data Model

The primary ClickHouse table is `developer_events`.

| Column | Data type | Description |
|---|---|---|
| `event_id` | String | Unique event identifier |
| `source` | LowCardinality(String) | Originating activity platform |
| `event_type` | LowCardinality(String) | Type of recorded event |
| `developer_id` | String | Developer identifier |
| `team_id` | String | Team identifier |
| `timestamp` | DateTime64(3, 'UTC') | Event timestamp |
| `metadata_json` | String | Additional event metadata |

The common event structure allows activity records from different sources to be stored and analyzed consistently.

## 8. Data Pipeline Workflow

The pipeline follows a sequence of dependent operations.

### Step 1: Event collection

Synthetic activity records are generated for GitHub, Slack, Jira, and IDE activity.

### Step 2: Validation

The records are checked against the shared event schema to identify invalid or incomplete data.

### Step 3: Processing

Python and Polars consolidate the source records into a common structure.

### Step 4: Parquet generation

The processed events are written into a unified Parquet file.

### Step 5: Database loading

The processed records are loaded into ClickHouse.

### Step 6: Verification

The pipeline checks that the expected records have been loaded successfully.

### Step 7: Analytics

SQL queries and the FastAPI backend provide access to summary information.

Apache Airflow manages the execution and dependencies of these pipeline tasks.

## 9. Analytics Methodology

### 9.1 Source activity

Events can be grouped by their source to understand how recorded activity is distributed across GitHub, Slack, Jira, and IDE activity.

### 9.2 Source transitions

A transition occurs when two consecutive recorded events for the same developer have different source values.

Transitions can be grouped by team and source pair.

For example:

```text
GitHub → Slack
Slack  → Jira
Jira   → IDE
```

These transitions indicate changes in recorded activity sources, not necessarily actual interruptions.

### 9.3 Event-gap classification

The current SQL analysis uses a threshold of **1,800 seconds (30 minutes)** to distinguish shorter from longer event gaps.

This is an exploratory assumption, not a validated cognitive-science threshold.

### 9.4 Interpretation limits

- A source transition does not prove an interruption occurred.
- A gap between events does not establish how long focus recovery took.
- Synthetic events do not represent observed employee behavior.
- Event counts are not equivalent to productivity or work quality.
- Team and developer summaries describe the generated dataset, not actual employee performance.

## 10. API Reference

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Basic API information |
| GET | `/health` | Health check |
| GET | `/api/v1/summary` | Event, developer, team and source counts |

When the local API is running, interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The summary endpoint provides the current analytical overview from ClickHouse.

## 11. Project Demonstration Guide

This section provides a practical sequence for demonstrating the currently implemented components of CogniStream.

### 11.1 Demonstrate event validation

Run:

```powershell
python ingestion/schemas/validate_events.py
```

Explain that the validation process checks the synthetic event records against the shared schema before they enter the processing pipeline.

### 11.2 Demonstrate data processing

Run:

```powershell
python processing/combine_events.py
```

Explain that Polars is used to combine and transform events from multiple sources into a common dataset.

The resulting Parquet file is:

```text
data/processed/all_events.parquet
```

### 11.3 Demonstrate ClickHouse storage

Connect to the local ClickHouse instance and inspect the database.

Example SQL:

```sql
SELECT count()
FROM developer_events;
```

To inspect activity distribution:

```sql
SELECT
    source,
    count() AS event_count
FROM developer_events
GROUP BY source
ORDER BY source;
```

Explain that ClickHouse stores the processed event records and supports analytical queries.

### 11.4 Demonstrate the Airflow pipeline

Start the local Docker Compose and Airflow environment.

Open the Airflow interface:

```text
http://localhost:8080
```

Locate the `cognistream_pipeline` DAG and inspect its tasks:

1. `validate_raw_events`
2. `combine_events_to_parquet`
3. `load_events_to_clickhouse`
4. `verify_clickhouse_load`

Explain that Airflow manages the pipeline workflow and ensures tasks execute in the required order.

### 11.5 Demonstrate the FastAPI backend

Start the backend from the project root:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Open the interactive documentation:

```text
http://127.0.0.1:8000/docs
```

Demonstrate these endpoints:

```text
GET /
GET /health
GET /api/v1/summary
```

Explain that the summary endpoint retrieves analytical information from ClickHouse.

### 11.6 Dashboard demonstration status

The React + Tremor.js dashboard is planned / in progress.

The current implementation exposes summary analytics through FastAPI, but the complete interactive frontend and dashboard integration are not yet complete.

The dashboard is intended to present information such as:

- Total recorded events.
- Unique developers and teams.
- Activity distribution by source.
- Activity trends over time.
- Source transitions and workflow indicators.

These are intended dashboard capabilities and should not be presented as completed frontend features until implemented.

## 12. Data Quality and Testing

The project includes:

- Event schema validation.
- ClickHouse data-quality queries.
- Processing tests.
- API tests.

Run the complete test suite from the repository root:

```powershell
python -m pytest -v
```

The latest recorded test checkpoint was:

```text
22 tests passed
```

Re-run the test suite after code changes to confirm the current result.

The API tests cover the root endpoint, health endpoint, and analytics summary response.

The summary test uses the local ClickHouse dataset, so ClickHouse must be available and populated when running the complete API test suite.

## 13. Repository Structure

```text
CogniStream/
│
├── airflow/
│   └── dags/
│       └── cognistream_pipeline.py
│
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
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
├── frontend/
│
├── ingestion/
│   ├── mock_apis/
│   └── schemas/
│
├── processing/
│   └── combine_events.py
│
├── sql/
│   ├── analytics/
│   └── schemas/
│
├── tests/
├── requirements.txt
└── README.md
```

Some directories are intended for future work and may not yet contain a complete implementation.

## 14. Getting Started

### 14.1 Prerequisites

- Python installed.
- Git installed.
- Project dependencies.
- A running ClickHouse instance.
- A local `.env` file configured with ClickHouse connection settings.
- Docker and Docker Compose for the local Airflow environment.

### 14.2 Clone the repository

```powershell
git clone https://github.com/SHREYASHRAW/CogniStream.git
cd CogniStream
```

### 14.3 Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 14.4 Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 14.5 Configure ClickHouse

Create a local `.env` file in the repository root:

```dotenv
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=cognistream
CLICKHOUSE_USER=cogni
CLICKHOUSE_PASSWORD=your_local_password
```

Replace the example password with your local ClickHouse password.

**Do not commit `.env` files, passwords, tokens, or other secrets to Git.**

### 14.6 Generate and process events

Generate or prepare the synthetic source files under `data/raw/`.

Run:

```powershell
python ingestion/schemas/validate_events.py
python processing/combine_events.py
```

### 14.7 Start the API

With the virtual environment active and ClickHouse available:

```powershell
python -m uvicorn backend.app.main:app --reload
```

Open:

- API root: `http://127.0.0.1:8000/`
- Health check: `http://127.0.0.1:8000/health`
- Analytics summary: `http://127.0.0.1:8000/api/v1/summary`
- Interactive documentation: `http://127.0.0.1:8000/docs`

### 14.8 Run tests

```powershell
python -m pytest -v
```

Ensure that ClickHouse is available and contains the expected test dataset before running the complete API test suite.

### 14.9 Run the Airflow pipeline

Use the project's local Docker Compose / Airflow setup.

Ensure ClickHouse is running and reachable from the Airflow container.

The DAG validates raw events, generates the Parquet dataset, loads events into ClickHouse, and verifies the load.

Connection values should be supplied through local environment configuration. Do not commit passwords or credentials.

## 15. Current Limitations

The current project has the following limitations:

- Data is synthetic and generated for development and testing.
- Ingestion uses local files rather than live external APIs.
- The dataset is small and intended for functional validation.
- Workflow indicators have not been validated against real developer workflows.
- The current API exposes a summary endpoint; more analytical endpoints are still needed.
- The React + Tremor.js dashboard is not yet complete.
- No claims of measured cognitive load, focus recovery, or productivity improvement are made.
- The current Airflow environment is intended for local development rather than production deployment.

## 16. Future Roadmap

The planned development activities are:

### Completed

- [x] Create synthetic GitHub, Slack, Jira, and IDE event generators.
- [x] Implement event schema validation.
- [x] Consolidate events using Python and Polars.
- [x] Generate a unified Parquet dataset.
- [x] Store unified events in ClickHouse.
- [x] Create baseline source activity and transition analytics.
- [x] Add automated processing and data-quality tests.
- [x] Orchestrate validation, processing, loading, and verification with Apache Airflow.
- [x] Expose summary analytics through FastAPI.
- [x] Add automated API tests.

### Planned / In progress

- [ ] Expand analytics endpoints and analytical edge-case tests.
- [ ] Refine session definitions and event-gap interpretation.
- [ ] Build the React + Tremor.js dashboard.
- [ ] Add dashboard integration and end-to-end tests.
- [ ] Complete reproducible end-to-end setup documentation.
- [ ] Explore additional workflow indicators and visualizations.

## 17. Project Philosophy

CogniStream is a learning and portfolio project focused on practical data engineering, analytical SQL, testing, and transparent interpretation of data.

The guiding principle is to measure what the data supports, document assumptions clearly, and avoid presenting workflow proxies as direct measurements of human cognition.

The project aims to demonstrate how activity data from multiple sources can be transformed into a unified analytical system using modern data engineering technologies.

---

**Project:** CogniStream
**Focus:** Developer Workflow Analytics and Data Engineering
**Backend:** Python + FastAPI
**Data Processing:** Python + Polars
**Database:** ClickHouse
**Orchestration:** Apache Airflow
**Frontend:** React + Tremor.js (planned / in progress)