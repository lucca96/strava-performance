import csv
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv


load_dotenv()

BASE_URL = "https://www.strava.com/api/v3"
OAUTH_URL = "https://www.strava.com/oauth/token"
DEFAULT_DATA_DIR = Path("data")
STREAM_KEYS = "time,heartrate,velocity_smooth,altitude,distance"


class ApiBudgetExceeded(RuntimeError):
    pass


class StravaClient:
    def __init__(self, data_dir=DEFAULT_DATA_DIR, max_calls=None, session=None):
        self.data_dir = Path(data_dir)
        self.cache_dir = self.data_dir / "cache"
        self.max_calls = int(max_calls or os.getenv("STRAVA_MAX_API_CALLS", "100"))
        self.session = session or requests.Session()
        self.calls_made = 0
        self.cache_hits = 0

    @property
    def calls_remaining(self):
        return max(0, self.max_calls - self.calls_made)

    def ensure_dirs(self):
        (self.cache_dir / "summary_pages").mkdir(parents=True, exist_ok=True)
        (self.cache_dir / "activities").mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _read_json(self, path):
        with open(path, "r", encoding="utf-8") as file:
            return json.load(file)

    def _write_json(self, path, data):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

    def _cache_get(self, path):
        if path.exists():
            self.cache_hits += 1
            data = self._read_json(path)
            if isinstance(data, dict) and data.get("_unavailable"):
                return None
            return data
        return None

    def _log_request(self, method, endpoint, activity_id, response):
        self.ensure_dirs()
        log_path = self.data_dir / "api_usage_log.csv"
        exists = log_path.exists()
        headers = getattr(response, "headers", {}) or {}

        with open(log_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(
                file,
                fieldnames=[
                    "timestamp_utc",
                    "method",
                    "endpoint",
                    "activity_id",
                    "status_code",
                    "rate_limit_limit",
                    "rate_limit_usage",
                    "calls_made",
                    "calls_remaining",
                ],
            )
            if not exists:
                writer.writeheader()
            writer.writerow(
                {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "method": method,
                    "endpoint": endpoint,
                    "activity_id": activity_id or "",
                    "status_code": getattr(response, "status_code", ""),
                    "rate_limit_limit": headers.get("X-RateLimit-Limit", ""),
                    "rate_limit_usage": headers.get("X-RateLimit-Usage", ""),
                    "calls_made": self.calls_made,
                    "calls_remaining": self.calls_remaining,
                }
            )

    def _request(self, method, url, endpoint, activity_id=None, **kwargs):
        if self.calls_made >= self.max_calls:
            raise ApiBudgetExceeded(f"API budget exhausted ({self.max_calls} calls)")

        self.calls_made += 1
        response = self.session.request(method, url, **kwargs)
        self._log_request(method, endpoint, activity_id, response)

        if response.status_code == 429:
            raise ApiBudgetExceeded("Strava rate limit exceeded")

        return response

    def _get_access_token(self):
        self.ensure_dirs()
        token_path = self.cache_dir / "token.json"
        if token_path.exists():
            token = self._read_json(token_path)
            if token.get("access_token") and token.get("expires_at", 0) > int(time.time()) + 60:
                self.cache_hits += 1
                return token["access_token"]

        payload = {
            "client_id": os.getenv("STRAVA_CLIENT_ID"),
            "client_secret": os.getenv("STRAVA_CLIENT_SECRET"),
            "refresh_token": os.getenv("STRAVA_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        }
        response = self._request("POST", OAUTH_URL, "oauth/token", data=payload)
        response.raise_for_status()
        token = response.json()
        self._write_json(token_path, token)
        return token["access_token"]

    def get_access_token(self):
        return self._get_access_token()

    def _auth_headers(self):
        return {"Authorization": f"Bearer {self._get_access_token()}"}

    def _get_cached_endpoint(
        self,
        cache_path,
        endpoint,
        activity_id=None,
        params=None,
        allow_unavailable=False,
        force_refresh=False,
    ):
        if not force_refresh:
            cached = self._cache_get(cache_path)
            if cached is not None or cache_path.exists():
                return cached

        response = self._request(
            "GET",
            f"{BASE_URL}/{endpoint}",
            endpoint,
            activity_id=activity_id,
            headers=self._auth_headers(),
            params=params,
        )

        if response.status_code != 200:
            if allow_unavailable:
                marker = {
                    "_unavailable": True,
                    "status_code": response.status_code,
                    "body": response.text,
                    "cached_at": datetime.now(timezone.utc).isoformat(),
                }
                self._write_json(cache_path, marker)
                return None
            response.raise_for_status()

        data = response.json()
        self._write_json(cache_path, data)
        return data

    def get_summary_page(self, page, per_page=30, force_refresh=False):
        cache_path = self.cache_dir / "summary_pages" / f"page_{page:03d}.json"
        return self._get_cached_endpoint(
            cache_path,
            "athlete/activities",
            params={"page": page, "per_page": per_page},
            force_refresh=force_refresh,
        )

    def get_activity_details(self, activity_id):
        cache_path = self.cache_dir / "activities" / str(activity_id) / "details.json"
        return self._get_cached_endpoint(cache_path, f"activities/{activity_id}", activity_id=activity_id)

    def get_activity_streams(self, activity_id):
        cache_path = self.cache_dir / "activities" / str(activity_id) / "streams.json"
        return self._get_cached_endpoint(
            cache_path,
            f"activities/{activity_id}/streams",
            activity_id=activity_id,
            params={"keys": STREAM_KEYS, "key_by_type": "true"},
            allow_unavailable=True,
        )

    def get_activity_laps(self, activity_id):
        cache_path = self.cache_dir / "activities" / str(activity_id) / "laps.json"
        return self._get_cached_endpoint(
            cache_path,
            f"activities/{activity_id}/laps",
            activity_id=activity_id,
            allow_unavailable=True,
        )
