# Football Data Platform

A lightweight Python ingestion project that pulls football match and standings data from the football-data.org API and stores the raw JSON payloads in a local filesystem structure for later analysis.

## Overview

This project currently focuses on collecting data for three competitions:

- Premier League (`PL`)
- La Liga (`PD`)
- Serie A (`SA`)

For each competition, it fetches:

- matches
- standings

The ingestion job stores raw responses under `data/raw/<competition>/<endpoint>/<date>/` so the project can be extended later with transformations, warehousing, analytics, or dashboards.

## Project Structure

```text
.
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env
├── data/
│   └── raw/
│       ├── PL/
│       │   ├── matches/
│       │   └── standings/
│       ├── PD/
│       │   ├── matches/
│       │   └── standings/
│       └── SA/
│           ├── matches/
│           └── standings/
├── src/
│   ├── __init__.py
│   └── ingest/
│       ├── __init__.py
│       ├── client.py
│       └── ingest_matches.py
└── tests/
```

## Requirements

- Python 3.12+
- A football-data.org API token
- Docker and Docker Compose (optional, for containerized runs)

## Setup

1. Clone the repository.
2. Create a `.env` file in the project root.
3. Add your API token using the environment variable expected by the client:

```env
FOOTBALL_DATA_TOKEN=your_token_here
```

## Local Run

Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Run the ingestion job:

```bash
python -m src.ingest.ingest_matches
```

## Docker Run

Build and start the ingestion service:

```bash
docker-compose up --build ingest
```

The application will read the token from `.env` and write raw payloads into `data/raw`.

## Behavior

The ingestion client:

- uses the `football-data.org` base URL
- throttles requests to avoid exceeding free-tier rate limits
- retries transient HTTP failures such as `429` and `5xx` responses
- writes each payload atomically to a timestamped JSON file

## Notes

- The project currently stores raw data only; no database or transformation layer is configured yet.
- The free tier of the football-data.org API has request limits, so the client includes a small delay between calls.
- The competition list is defined in `src/ingest/ingest_matches.py` and can be extended if additional leagues are needed.

## License

This project does not include a license file yet. Add one if you plan to distribute it publicly.
