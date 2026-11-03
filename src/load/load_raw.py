import json
import logging
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import Json

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

RAW_DIR = Path("data/raw")

DDL = """
CREATE SCHEMA IF NOT EXISTS raw;

CREATE TABLE IF NOT EXISTS raw.matches (
    match_id         BIGINT PRIMARY KEY,
    competition_code TEXT NOT NULL,
    payload          JSONB NOT NULL,
    source_file      TEXT NOT NULL,
    loaded_at        TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.standings (
    competition_code TEXT NOT NULL,
    snapshot_date    DATE NOT NULL,
    payload          JSONB NOT NULL,
    source_file      TEXT NOT NULL,
    loaded_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (competition_code, snapshot_date)
);
"""


def connect():
    return psycopg2.connect(
        host=os.environ.get("POSTGRES_HOST", "localhost"),
        port=os.environ.get("POSTGRES_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
    )


def load_matches(cur, path, code):
    data = json.loads(path.read_text(encoding="utf-8"))
    matches = data.get("matches", [])
    for m in matches:
        cur.execute(
            """
            INSERT INTO raw.matches (match_id, competition_code, payload, source_file)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (match_id) DO UPDATE
               SET payload = EXCLUDED.payload,
                   source_file = EXCLUDED.source_file,
                   loaded_at = now()
            """,
            (m["id"], code, Json(m), str(path)),
        )
    return len(matches)


def load_standings(cur, path, code):
    data = json.loads(path.read_text(encoding="utf-8"))
    snapshot_date = path.parent.name  # folder is named YYYY-MM-DD
    cur.execute(
        """
        INSERT INTO raw.standings (competition_code, snapshot_date, payload, source_file)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (competition_code, snapshot_date) DO UPDATE
           SET payload = EXCLUDED.payload,
               source_file = EXCLUDED.source_file,
               loaded_at = now()
        """,
        (code, snapshot_date, Json(data), str(path)),
    )
    return 1


LOADERS = {"matches": load_matches, "standings": load_standings}


def main():
    conn = connect()
    try:
        with conn, conn.cursor() as cur:  # one transaction: all or nothing
            cur.execute(DDL)
            for comp_dir in sorted(p for p in RAW_DIR.iterdir() if p.is_dir()):
                for endpoint, loader in LOADERS.items():
                    # sorted by date/time: the latest file of a day wins
                    for path in sorted((comp_dir / endpoint).glob("*/*.json")):
                        n = loader(cur, path, comp_dir.name)
                        log.info("%s/%s: %s -> %d rows upserted", comp_dir.name, endpoint, path.name, n)
    finally:
        conn.close()


if __name__ == "__main__":
    main()