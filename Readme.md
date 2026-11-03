# Football Data Platform

A Python data pipeline that ingests football match and standings data from the [football-data.org](https://www.football-data.org/) API, stores raw records in PostgreSQL, and uses dbt to build analytics models.

## Data pipeline

The project currently collects Premier League (`PL`), La Liga (`PD`), and Serie A (`SA`) data:

1. **Ingest** match and standings responses from football-data.org. Requests are throttled and transient HTTP failures are retried. Raw JSON responses are saved under `data/raw/<competition>/<endpoint>/<date>/`.
2. **Load** the raw files into PostgreSQL's `raw` schema. Match records and dated standings snapshots are upserted, so the loader can be run again safely.
3. **Transform** the raw tables with dbt. Staging models expose match and standings fields; the league-table mart calculates standings from finished regular-season matches.
4. **Test** model constraints and finished-match scores, and compare the calculated league table with the latest API standings snapshot.

## Requirements

- Python 3.12+
- A football-data.org API token
- Docker and Docker Compose

## Setup

Create a local `.env` file from the example and add your API token and PostgreSQL settings:

```bash
cp .env.example .env
```

```env
FOOTBALL_DATA_TOKEN=your_token_here
POSTGRES_USER=football
POSTGRES_PASSWORD=your_password
POSTGRES_DB=football
```

Keep `.env` private; it contains credentials.

## Run the pipeline with Docker Compose

Start PostgreSQL and wait for its health check:

```bash
docker compose up -d postgres
```

Run the steps in order so the raw files exist before loading and the tables exist before dbt runs:

```bash
docker compose run --build --rm ingest
docker compose run --build --rm load
docker compose run --build --rm dbt
```

The ingestion service writes files to `data/raw/`. The loader creates the `raw.matches` and `raw.standings` tables and loads those files. dbt builds staging views in the `analytics` schema and the `mart_league_table` table. `dbt build` runs the configured model tests as well as the models.

Stop PostgreSQL when finished:

```bash
docker compose down
```

To remove the persisted PostgreSQL data volume as well, use `docker compose down -v`.

## Run ingestion locally

You can run just the API ingestion step without Docker:

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python -m src.ingest.ingest_matches
```

The local run needs `FOOTBALL_DATA_TOKEN` set in the environment (or loaded from `.env` by your shell or IDE). To load into PostgreSQL or run dbt, use the Docker Compose steps above.

## Project structure

```text
.
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── data/                       # Local raw JSON files (not committed)
├── dbt/
│   ├── models/
│   │   ├── staging/            # Staging views and source definitions
│   │   └── marts/              # Analytics tables
│   ├── tests/                  # Singular dbt data tests
│   └── profiles.yml
└── src/
    ├─�� ingest/                 # API client and ingestion job
    └── load/                   # PostgreSQL raw-data loader
```

## Notes

- The API's free tier has request limits; ingestion includes a delay between calls.
- The league-table mart includes finished matches in the `REGULAR_SEASON` stage and ranks teams by points, goal difference, then goals scored.
- The API-versus-mart standings comparison is configured as a warning because snapshots or results may not always match exactly.

## License

This project does not include a license file yet. Add one if you plan to distribute it publicly.
