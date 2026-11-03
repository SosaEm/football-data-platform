import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from .client import FootballDataClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

COMPETITIONS = ["PL", "PD", "SA"]  # Premier League, La Liga, Serie A
ENDPOINTS = ["matches", "standings"]
RAW_DIR = Path("data/raw")


def save_raw(payload, competition, endpoint):
    now = datetime.now(timezone.utc)
    folder = RAW_DIR / competition / endpoint / now.strftime("%Y-%m-%d")
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{now.strftime('%H%M%S')}.json"
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    tmp.replace(path)  # atomic: no half-written files
    return path


def main():
    client = FootballDataClient()
    for code in COMPETITIONS:
        for endpoint in ENDPOINTS:
            data = client.get(f"/competitions/{code}/{endpoint}")
            path = save_raw(data, code, endpoint)
            log.info("Saved %s/%s -> %s", code, endpoint, path)


if __name__ == "__main__":
    main()