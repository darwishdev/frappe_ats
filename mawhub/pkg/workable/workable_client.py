"""
WorkableApiClient
=================
ETL layer for syncing Workable data into Frappe/ERPNext doctypes.

Covered endpoints
-----------------
  GET  /jobs                                    list_jobs()
  GET  /jobs/{shortcode}                        get_job()
  GET  /stages                                  list_stages()
  GET  /candidates                              list_candidates()
  GET  /jobs/{shortcode}/candidates             list_job_candidates()
  GET  /jobs/{shortcode}/candidates/{id}        get_candidate()
  GET  /jobs/{shortcode}/candidates/{id}/activities  get_candidate_activities()
  GET  /subscriptions                           list_subscriptions()
  POST /subscriptions                           create_subscription()
  DELETE /subscriptions/{id}                    delete_subscription()

Pagination
----------
All list methods that return a ``paging.next`` cursor support automatic
pagination via ``paginate=True``.  The raw ``paging`` dict is also returned
so callers can implement manual pagination if needed.

Usage
-----
    client = WorkableApiClient(
        subdomain="lucidya",
        api_token="BexiVhSqQG0InFOVf2LGFGldTAZon5yuHlfHD9PHc5s",
    )
    jobs = client.list_jobs(state="published", paginate=True)
"""

from __future__ import annotations

import time
from typing import Any
from urllib.parse import urlparse, parse_qs

import httpx

from mawhub.pkg.workable.workable_types import (
    WorkableActivitiesResponse,
    WorkableActivity,
    WorkableCandidate,
    WorkableEvent,
    WorkableEventType,
    WorkableJob,
    WorkableJobState,
    WorkableStage,
    WorkableStagesResponse,
    WorkableSubscription,
    WorkableSubscriptionsResponse,
)

_DEFAULT_LIMIT = 50
_MAX_PAGES = 200  # safety cap for paginate=True


class WorkableApiError(Exception):
    """Raised when Workable returns a non-2xx response."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"Workable API error {status_code}: {message}")


class WorkableApiClient:
    """Thin HTTP client for the Workable SPI v3 API."""

    def __init__(self, subdomain: str, api_token: str, timeout: float = 30.0) -> None:
        self._base_url = f"https://{subdomain}.workable.com/spi/v3"
        self._client = httpx.Client(
            headers={
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json",
            },
            timeout=timeout,
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, path: str, params: dict[str, Any] | None = None, _retry: int = 3) -> dict[str, Any]:
        url = f"{self._base_url}/{path.lstrip('/')}"
        response: httpx.Response | None = None
        for attempt in range(_retry):
            response = self._client.get(url, params=params)
            if response.status_code == 429 and attempt < _retry - 1:
                retry_after = int(response.headers.get("Retry-After", 10))
                time.sleep(retry_after)
                continue
            self._raise_for_status(response)
            return response.json()
        if response is not None:
            self._raise_for_status(response)
        raise WorkableApiError(0, "No response received after retries")

    def _post(self, path: str, body: dict[str, Any]) -> dict[str, Any]:
        url = f"{self._base_url}/{path.lstrip('/')}"
        response = self._client.post(url, json=body)
        self._raise_for_status(response)
        return response.json()

    def _delete(self, path: str) -> None:
        url = f"{self._base_url}/{path.lstrip('/')}"
        response = self._client.delete(url)
        self._raise_for_status(response)

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        if response.status_code >= 400:
            try:
                detail = response.json().get("message", response.text)
            except Exception:
                detail = response.text
            raise WorkableApiError(response.status_code, detail)

    @staticmethod
    def _extract_since_id(next_url: str | None) -> str | None:
        """Parse the ``since_id`` cursor out of a paging.next URL."""
        if not next_url:
            return None
        qs = parse_qs(urlparse(next_url).query)
        values = qs.get("since_id", [])
        return values[0] if values else None

    # ------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------

    def list_jobs(
        self,
        *,
        state: WorkableJobState | None = None,
        limit: int = _DEFAULT_LIMIT,
        since_id: str | None = None,
        updated_after: str | None = None,
        include_description: bool = False,
        paginate: bool = False,
    ) -> list[WorkableJob]:
        """Return jobs, optionally fetching all pages automatically."""
        params: dict[str, Any] = {"limit": limit}
        if state:
            params["state"] = state
        if since_id:
            params["since_id"] = since_id
        if updated_after:
            params["updated_after"] = updated_after
        if include_description:
            params["include_fields"] = "description,full_description,requirements,benefits"

        return self._paginate_list("jobs", "jobs", params, paginate)

    def get_job(self, shortcode: str) -> WorkableJob:
        """Return full detail for a single job (includes description fields)."""
        data = self._get(f"jobs/{shortcode}")
        return data  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Stages
    # ------------------------------------------------------------------

    def list_stages(self) -> list[WorkableStage]:
        """Return all pipeline stages for the account."""
        data: WorkableStagesResponse = self._get("stages")  # type: ignore[assignment]
        return data["stages"]

    # ------------------------------------------------------------------
    # Candidates
    # ------------------------------------------------------------------

    def list_candidates(
        self,
        *,
        stage: str | None = None,
        limit: int = _DEFAULT_LIMIT,
        since_id: str | None = None,
        updated_after: str | None = None,
        paginate: bool = False,
    ) -> list[WorkableCandidate]:
        """Return candidates across all jobs."""
        params: dict[str, Any] = {"limit": limit}
        if stage:
            params["stage"] = stage
        if since_id:
            params["since_id"] = since_id
        if updated_after:
            params["updated_after"] = updated_after

        return self._paginate_list("candidates", "candidates", params, paginate)

    def list_job_candidates(
        self,
        shortcode: str,
        *,
        stage: str | None = None,
        limit: int = _DEFAULT_LIMIT,
        since_id: str | None = None,
        updated_after: str | None = None,
        paginate: bool = False,
    ) -> list[WorkableCandidate]:
        """Return candidates for a specific job."""
        params: dict[str, Any] = {"limit": limit}
        if stage:
            params["stage"] = stage
        if since_id:
            params["since_id"] = since_id
        if updated_after:
            params["updated_after"] = updated_after

        return self._paginate_list(
            f"jobs/{shortcode}/candidates", "candidates", params, paginate
        )

    def get_candidate(self, shortcode: str, candidate_id: str) -> WorkableCandidate:
        """Return full profile for a single candidate."""
        data = self._get(f"jobs/{shortcode}/candidates/{candidate_id}")
        return data.get("candidate", data)  # type: ignore[return-value]

    def get_candidate_activities(
        self, shortcode: str, candidate_id: str
    ) -> list[WorkableActivity]:
        """Return activity timeline for a candidate (stage moves, comments, etc.)."""
        data: WorkableActivitiesResponse = self._get(  # type: ignore[assignment]
            f"jobs/{shortcode}/candidates/{candidate_id}/activities"
        )
        return data.get("activities", [])  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def list_events(
        self,
        *,
        event_type: str = "interview",
        limit: int = _DEFAULT_LIMIT,
        since_id: str | None = None,
        include_cancelled: bool = False,
        paginate: bool = False,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[WorkableEvent]:
        """Return calendar events (interviews by default)."""
        params: dict[str, Any] = {
            "type": event_type,
            "limit": limit,
            "include_cancelled": str(include_cancelled).lower(),
        }
        if since_id:
            params["since_id"] = since_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        return self._paginate_list("events", "events", params, paginate)

    # ------------------------------------------------------------------
    # Subscriptions (webhooks)
    # ------------------------------------------------------------------

    def list_subscriptions(self) -> list[WorkableSubscription]:
        data: WorkableSubscriptionsResponse = self._get("subscriptions")  # type: ignore[assignment]
        return data.get("subscriptions", [])  # type: ignore[return-value]

    def create_subscription(
        self,
        event: WorkableEventType,
        target_url: str,
        *,
        stage_slug: str | None = None,
        job_shortcode: str | None = None,
    ) -> WorkableSubscription:
        """Register a webhook for a Workable event."""
        body: dict[str, Any] = {"event": event, "url": target_url}
        if stage_slug:
            body["stage_slug"] = stage_slug
        if job_shortcode:
            body["job_shortcode"] = job_shortcode
        data = self._post("subscriptions", body)
        return data.get("subscription", data)  # type: ignore[return-value]

    def delete_subscription(self, subscription_id: int) -> None:
        """Remove a webhook subscription."""
        self._delete(f"subscriptions/{subscription_id}")

    # ------------------------------------------------------------------
    # Pagination helper
    # ------------------------------------------------------------------

    def _paginate_list(
        self,
        path: str,
        list_key: str,
        params: dict[str, Any],
        paginate: bool,
    ) -> list[Any]:
        data = self._get(path, params)
        results: list[Any] = list(data.get(list_key, []))

        if not paginate:
            return results

        page = 1
        while page < _MAX_PAGES:
            next_url: str | None = data.get("paging", {}).get("next")
            since_id = self._extract_since_id(next_url)
            if not since_id:
                break
            params = {**params, "since_id": since_id}
            data = self._get(path, params)
            batch = data.get(list_key, [])
            if not batch:
                break
            results.extend(batch)
            page += 1

        return results

    # ------------------------------------------------------------------
    # Context-manager support
    # ------------------------------------------------------------------

    def __enter__(self) -> "WorkableApiClient":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()
