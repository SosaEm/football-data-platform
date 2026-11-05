import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

from .client import FootballDataClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

COMPETITIONS = ["PL", "PD", "SA", "CL"]
ENDPOINTS = {  # endpoint -> query params
    "matches": None,
    "standings": None,
    "scorers": {"limit": 100},
}
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
    saved = 0
    for code in COMPETITIONS:
        for endpoint, params in ENDPOINTS.items():
            try:
                data = client.get(f"/competitions/{code}/{endpoint}", params=params)
            except requests.HTTPError as exc:
                # e.g. an endpoint not included in the free plan: skip it, keep going
                log.warning("Skipping %s/%s: %s", code, endpoint, exc)
                continue
            path = save_raw(data, code, endpoint)
            saved += 1
            log.info("Saved %s/%s -> %s", code, endpoint, path)

    if saved == 0:
        # e.g. an invalid token would make every call fail: do not report success
        raise RuntimeError("Nothing was ingested: check the API token and access")


if __name__ == "__main__":
    main()