# Football Data Platform

End-to-end data pipeline: ingests match and standings data from the
football-data.org API, stores it raw in PostgreSQL, and models it with dbt.

## Architecture
API -> Python ingestion (rate limiting, retries) -> raw JSON files
    -> PostgreSQL `raw` schema (idempotent upserts)
    -> dbt staging views -> dbt marts (league table) + data tests

## Tech stack
Python · PostgreSQL · dbt · Docker Compose

## How to run
1. Copy `.env.example` to `.env` and fill in your API token and DB credentials.
2. `docker compose up -d postgres`
3. `docker compose run --rm ingest`
4. `docker compose run --rm load`
5. `docker compose run --rm dbt build`

## How to restart
1. `cd airflow`
2. `docker compose down`
3. `cd ..`
4. `docker compose down`
5. `docker compose up -d postgres`
6. `cd airflow`
7. `docker compose up -d`

## Design decisions
- **Raw layer is kept as received** (JSON + JSONB) so models can be rebuilt.
- **Idempotent loads:** re-running the loader never duplicates rows (upserts).
- **Rate limiting and retries** to respect the free API tier (10 requests/min).
- **Data quality:** dbt tests plus a reconciliation test comparing the computed
  league table against the API's own standings.

## Limitations
- Free API tier: current season only, limited competitions.
- Tie-breaker rules are simplified (no head-to-head).

## Data source
Data provided by football-data.org. Please check their terms of use.

## Orchestration
An Airflow DAG (`football_pipeline`) runs daily: `ingest >> load_raw >> dbt_build`,
with 2 retries and a 5-minute delay per task. See `airflow/`.

## Design notes
- **LocalExecutor** instead of the default Celery stack: the DAG only runs
  shell tasks, so Redis and extra workers were unnecessary (lower memory).
- **dbt in its own virtualenv** inside the Airflow image to avoid dependency
  conflicts with Airflow.
- **Raw data stored in a Docker volume**, not a Windows bind mount, to avoid
  file-permission errors on Docker Desktop.
- **Airflow reaches the project database via `host.docker.internal`**;
  in production a shared network or managed database would be used.

## Known limitations
- BashOperator with mounted code is simple for local use; production would use
  containerized tasks (DockerOperator / Kubernetes).

## Continuous Integration
GitHub Actions runs on every push and pull request: it starts a clean Ubuntu
runner with a throwaway PostgreSQL service, loads small fixture files into the
raw layer and runs `dbt build`.

- **Fixture data instead of the live API:** deterministic results, no API token
  needed in CI and no rate-limit issues.
- **Clean environment:** catches missing dependencies or uncommitted files that
  would otherwise "work on my machine".
- **Host is `localhost`:** the job runs directly on the runner and the service
  container publishes its port there (in Docker Compose, services reach each
  other by service name).

Limitation: CI does not exercise the live API ingestion or the Airflow DAG.

![CI](https://github.com/SosaEm/football-data-platform/actions/workflows/ci.yml/badge.svg)
