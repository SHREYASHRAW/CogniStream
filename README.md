# CogniStream
### Developer Flow-State & Cognitive Load Analytics

CogniStream is a data engineering and analytics project designed to explore developer workflows, cross-platform activity, and potential context switching.

Rather than relying on simplistic productivity indicators such as lines of code or tickets closed, CogniStream brings together synthetic activity events from GitHub, Slack, Jira, and IDE activity into a unified analytical dataset.

The project explores how event sequences, source transitions, and time gaps can provide useful **workflow indicators** for engineering teams.

> **Project status:** Data ingestion simulation, schema validation, data processing, ClickHouse storage, baseline SQL analytics, and automated tests are implemented. Workflow indicators are exploratory proxies, not direct measurements of cognitive load or productivity.

---

## Table of Contents

- [Problem Statement](#problem-statement)
- [Project Objectives](#project-objectives)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Current Implementation](#current-implementation)
- [Analytics Methodology](#analytics-methodology)
- [Data Quality and Testing](#data-quality-and-testing)
- [Repository Structure](#repository-structure)
- [Getting Started](#getting-started)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)

---

## Problem Statement

Software engineering work often spans multiple tools. A developer may switch between code changes, messages, issue updates, and local IDE activity throughout a work session.

These activities are distributed across systems, making it difficult to understand the sequence of work and identify patterns of cross-tool activity.

CogniStream aims to establish a unified event data foundation and explore questions such as:

- How is activity distributed across developer tools?
- How frequently do recorded events transition between sources?
- How do event-to-event time gaps vary across teams and source transitions?
- How could these indicators support a future developer workflow analytics dashboard?

The project does not assume that every source transition is an interruption or that every time gap represents lost productivity.

## Project Objectives

1. Generate representative developer activity events from multiple simulated sources.
2. Validate events against a consistent schema.
3. Consolidate events into a unified dataset using Python and Polars.
4. Store structured events in ClickHouse for analytical queries.
5. Build SQL summaries for activity distribution and source transitions.
6. Add automated tests for processing behavior and data quality.
7. Extend the pipeline with orchestration, an API, and a dashboard.

---

## Architecture

### Current pipeline

```text
Synthetic Event Generators
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
          |
          v
       SQL Analytics
```

### Planned extensions

```text
Apache Airflow
      |
      v
Scheduled Ingestion and Processing
      |
      v
ClickHouse Analytics
      |
      v
FastAPI Backend
      |
      v
React + Tremor.js Dashboard
```

The first diagram represents the implemented workflow. The second shows planned components and is not a claim that the complete production architecture is already deployed.

---

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Event generation, validation, and processing |
| JSON / JSONL | Synthetic event records and intermediate files |
| Polars | Data transformation and Parquet generation |
| Parquet | Columnar storage for processed events |
| ClickHouse | Analytical event storage and SQL queries |
| SQL | Activity summaries and source-transition analysis |
| pytest | Automated testing |
| Git and GitHub | Version control and project documentation |

**Planned:** Apache Airflow for orchestration, FastAPI for analytics endpoints, and React with Tremor.js for the dashboard.

---

## Current Implementation

### 1. Synthetic event generation

Four generators simulate activity from:

- GitHub
- Slack
- Jira
- IDE activity

The generators produce JSONL records using a shared event structure. Developer and team identifiers are associated through a consistent mapping.

### 2. Event schema validation

A JSON schema and validation script check incoming records before processing.

The latest recorded validation checkpoint reported:

- GitHub: 30 valid events
- Slack: 30 valid events
- Jira: 30 valid events
- IDE: 30 valid events
- **Total: 120 valid events**

### 3. Data processing

The Python processing pipeline:

- Reads the four required JSONL input files.
- Parses JSON records and handles blank lines.
- Reports missing files and malformed JSON.
- Extracts consistent event fields.
- Serializes metadata into a normalized JSON string.
- Converts timestamps to UTC-aware datetimes.
- Sorts events chronologically.
- Writes a compressed Parquet dataset.

### 4. ClickHouse storage

The unified event dataset is stored in the `developer_events` table in the `cognistream` database.

At the latest recorded checkpoint, the table contained 120 events with 120 unique event IDs. Data-quality checks reported no empty developer or team identifiers and no unexpected event sources.

### 5. SQL analytics

The current SQL analytics include:

- **Source activity summary:** event totals, active developers, and timestamp ranges by source.
- **Source transition summary:** transitions grouped by team and source pair, including counts and event-to-event time gaps.
- **Potential context switches:** chronological source changes for individual developers.

These queries establish a baseline for exploratory analysis and future dashboard development.

---

## Analytics Methodology

CogniStream currently uses event sequences and time gaps as descriptive workflow indicators.

### Source transitions

A transition occurs when two consecutive recorded events for the same developer and team have different source values.

### Event-gap classification

The current transition summary uses a configurable initial threshold of **1,800 seconds (30 minutes)** to distinguish shorter from longer event gaps.

This is an exploratory analytical assumption, not a validated cognitive-science threshold.

### Important interpretation limits

- A source transition does not prove that an interruption occurred.
- A gap between events does not establish how long a developer needed to regain focus.
- Synthetic events do not represent observed employee behavior.
- Event counts are not equivalent to productivity or work quality.
- The current dataset is too small and synthetic to support real-world performance conclusions.

The objective is to build a sound data foundation and transparent analytical definitions before introducing more advanced interpretations.

---

## Data Quality and Testing

CogniStream uses `pytest` to test event loading, processing, and processed-data integrity.

The latest recorded test checkpoint passed **11 automated tests**:

| Test area | Coverage |
|---|---|
| Event loading | Reads all four sources |
| Field integrity | Preserves identifiers and metadata |
| Input handling | Skips blank lines and detects missing files |
| Error handling | Detects malformed JSON |
| Processing output | Verifies Parquet creation and required columns |
| Event uniqueness | Checks for duplicate event IDs |
| Identifier quality | Checks developer and team identifiers |
| Source integrity | Verifies expected event sources |
| Timestamp quality | Checks non-null and sorted timestamps |

Run the current suite from the project root:

```powershell
python -m pytest -v
```

The documented result reflects the last verified test run. Re-run the suite after making changes to confirm the current result.

---

## Repository Structure

```text
CogniStream/
├── airflow/                  # Planned workflow orchestration
├── backend/                  # Planned FastAPI backend
├── data/
│   ├── raw/                  # Local synthetic input events
│   └── processed/            # Generated Parquet dataset
├── docs/                     # Project documentation
├── frontend/                 # Planned React dashboard
├── ingestion/
│   ├── mock_apis/            # Synthetic source generators
│   └── schemas/              # Event schema and validation
├── processing/
│   └── combine_events.py     # Unified event processing
├── sql/
│   ├── analytics/             # Analytical SQL queries
│   └── schemas/               # ClickHouse table definitions
├── tests/
│   ├── test_combine_events.py
│   └── test_data_quality.py
├── requirements.txt
└── README.md
```

Some directories represent planned components and may not contain a completed implementation yet.

---

## Getting Started

### Prerequisites

- Python compatible with the project's installed dependencies
- Git
- A running ClickHouse instance for database analytics
- The project's Python dependencies installed in a virtual environment

### 1. Clone the repository

```powershell
git clone https://github.com/SHREYASHRAW/CogniStream.git
cd CogniStream
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Prepare the synthetic event data

Generate the four source JSONL files using the scripts under `ingestion/mock_apis/`.

Validate the generated events:

```powershell
python ingestion/schemas/validate_events.py
```

### 5. Process the events

```powershell
python processing/combine_events.py
```

The processing script writes the consolidated dataset to:

```text
data/processed/all_events.parquet
```

### 6. Run automated tests

```powershell
python -m pytest -v
```

### 7. Run SQL analytics

Start and configure ClickHouse using your local development setup, load the processed events into the `developer_events` table, and execute the queries under `sql/analytics/`.

Connection details should be supplied through local environment configuration. Do not commit passwords, tokens, or other secrets to the repository.

---

## Current Limitations

- Data is synthetic and generated for development and testing.
- Ingestion currently uses local event files rather than live external APIs.
- The current dataset is small and intended for functional validation.
- SQL analytics are exploratory and have not been validated against real developer workflows.
- Airflow orchestration, FastAPI endpoints, and the React dashboard remain planned extensions.
- No claims of measured cognitive load, focus recovery, or productivity improvement are made.

---

## Roadmap

- [x] Create synthetic GitHub, Slack, Jira, and IDE event generators.
- [x] Implement schema validation.
- [x] Consolidate events using Python and Polars.
- [x] Store the unified events in ClickHouse.
- [x] Create baseline source activity and transition analytics.
- [x] Add initial automated processing and data-quality tests.
- [ ] Expand tests for analytical edge cases and SQL results.
- [ ] Refine session definitions and event-gap interpretation.
- [ ] Orchestrate ingestion and processing with Apache Airflow.
- [ ] Expose aggregated analytics through FastAPI.
- [ ] Build an interactive React and Tremor.js dashboard.
- [ ] Add documentation and reproducible end-to-end setup instructions.

---

## Project Philosophy

CogniStream is being developed as a learning and portfolio project focused on practical data engineering, analytical SQL, testing, and transparent interpretation of data.

The guiding principle is to measure what the data actually supports, document assumptions clearly, and avoid presenting workflow proxies as direct measures of human cognition.
