import logging
import os
import time

import requests

log = logging.getLogger(__name__)

BASE_URL = "https://api.football-data.org/v4"
MIN_INTERVAL = 6.5  # free tier: 10 requests/min -> 1 request every 6 s, with margin


class FootballDataClient:
    def __init__(self, token=None, min_interval=MIN_INTERVAL, max_retries=5):
        self.token = token or os.environ["FOOTBALL_DATA_TOKEN"]
        self.session = requests.Session()
        self.session.headers.update({"X-Auth-Token": self.token})
        self.min_interval = min_interval
        self.max_retries = max_retries
        self._last_call = 0.0

    def _throttle(self):
        wait = self.min_interval - (time.monotonic() - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def get(self, path, params=None):
        url = f"{BASE_URL}{path}"
        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            try:
                resp = self.session.get(url, params=params, timeout=30)
            except requests.RequestException as exc:
                log.warning("Network error on %s (attempt %d): %s", path, attempt, exc)
                time.sleep(2 ** attempt)
                continue

            if resp.status_code == 200:
                return resp.json()

            if resp.status_code == 429 or resp.status_code >= 500:
                try:
                    wait = float(resp.headers.get("Retry-After", ""))
                except ValueError:
                    wait = 5 * 2 ** attempt
                log.warning("HTTP %d on %s, retrying in %.0fs", resp.status_code, path, wait)
                time.sleep(wait)
                continue

            resp.raise_for_status()  # 4xx (bad token, no access): do not retry

        raise RuntimeError(f"Failed after {self.max_retries} attempts: {path}")