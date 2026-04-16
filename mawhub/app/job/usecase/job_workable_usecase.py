from datetime import datetime, timezone
from typing import Any, Protocol, cast

import frappe

from mawhub.app.job.adapter.job_adapter import JobAdapterInterface
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.mawhub.doctype.workable_job.workable_job import WorkableJobDBModel
from mawhub.pkg.workable.workable_client import WorkableApiClient
from mawhub.pkg.workable.workable_types import WorkableJobState


# Jobs in these states carry no active candidates — skip their candidate sync.
_INACTIVE_JOB_STATES = frozenset({"closed", "archived"})


class JobWorkableUsecaseInterface(Protocol):
    def sync_stages(self) -> dict[str, str]: ...
    def sync_jobs(
        self,
        *,
        state: WorkableJobState,
        updated_after: str | None,
        paginate: bool,
    ) -> list[str]: ...
    def sync_candidates_for_job(
        self,
        shortcode: str,
        *,
        updated_after: str | None,
        stage_lookup: dict[str, str] | None,
    ) -> int: ...
    def sync_events(
        self,
        *,
        event_type: str,
        include_cancelled: bool,
        since_id: str | None,
        paginate: bool,
    ) -> int: ...
    def sync_all(
        self,
        *,
        state: WorkableJobState,
        updated_after: str | None,
    ) -> dict[str, Any]: ...



class JobWorkableUsecase:
    repo: JobRepoInterface
    adapter: JobAdapterInterface
    workable_client: WorkableApiClient

    def __init__(
        self,
        repo: JobRepoInterface,
        adapter: JobAdapterInterface,
        workable_client: WorkableApiClient,
    ):
        self.repo = repo
        self.adapter = adapter
        self.workable_client = workable_client

    # ------------------------------------------------------------------
    # Timestamp / cursor helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _last_sync_ts(doctype: str) -> str | None:
        """
        Return the maximum ``workable_updated_at`` stored in *doctype* as a
        Workable-compatible ISO-8601 string (``YYYY-MM-DDTHH:MM:SSZ``).

        Used to build incremental ``updated_after`` windows so subsequent
        sync runs only pull records that changed since the last run.
        Returns None when the table is empty or the column is unset,
        which triggers a full fetch on the next call.
        """
        rows = list(frappe.db.sql(
            f"SELECT MAX(workable_updated_at) FROM `tab{doctype}`"
        ) or [])
        ts = rows[0][0] if rows else None  # type: ignore[index]
        if not ts:
            return None
        # Frappe stores datetimes as "YYYY-MM-DD HH:MM:SS"; convert to ISO-8601.
        return str(ts).replace(" ", "T") + "Z"

    @staticmethod
    def _last_event_since_id() -> str | None:
        """
        Return the max event ID currently stored in Workable Event.
        Workable event IDs are sequential hex strings (e.g. ``438c02``),
        so the max ID acts as a reliable cursor for incremental fetches.
        Returns None when the table is empty (triggers a full fetch).
        """
        rows = list(frappe.db.sql(
            "SELECT MAX(name) FROM `tabWorkable Event`"
        ) or [])
        val = rows[0][0] if rows else None  # type: ignore[index]
        return str(val) if val else None

    # ------------------------------------------------------------------
    # Stages
    # ------------------------------------------------------------------

    def sync_stages(self) -> dict[str, str]:
        """
        Fetch all pipeline stages from Workable and upsert into Frappe.
        Returns a name→slug lookup that can be reused for candidate sync.
        """
        stages = self.workable_client.list_stages()
        for stage in stages:
            self.repo.workable_stage.create_or_update(
                self.adapter.workable.stage_to_db(stage)
            )
        return {s["name"]: s["slug"] for s in stages}

    # ------------------------------------------------------------------
    # Jobs
    # ------------------------------------------------------------------

    def sync_jobs(
        self,
        *,
        state: WorkableJobState = "published",
        updated_after: str | None = None,
        paginate: bool = False,
    ) -> list[str]:
        """
        Fetch jobs from Workable and upsert into Frappe (with stage rows).
        Closed and archived jobs are skipped even if the API returns them.
        Returns the list of synced shortcodes.
        """
        stages = self.workable_client.list_stages()
        jobs = self.workable_client.list_jobs(
            state=state,
            updated_after=updated_after,
            include_description=True,
            paginate=paginate,
        )
        shortcodes: list[str] = []
        for job in jobs:
            job_state = job.get("state") or ""
            if job_state in _INACTIVE_JOB_STATES:
                print(f"[WorkableSync] Skipping job {job['shortcode']} (state={job_state})")
                continue
            self.repo.workable_job.create_or_update(
                self.adapter.workable.job_to_db(job, stages)
            )
            shortcodes.append(job["shortcode"])
        return shortcodes

    # ------------------------------------------------------------------
    # Candidates
    # ------------------------------------------------------------------

    def sync_candidates_for_job(
        self,
        shortcode: str,
        *,
        updated_after: str | None = None,
        stage_lookup: dict[str, str] | None = None,
    ) -> int:
        """
        Fetch every candidate for *shortcode*, upsert each into Frappe,
        then rebuild the job's candidates child table.

        Skips the entire job if it is locally marked closed or archived —
        there is no value in pulling candidates for a job that is no longer
        active.  Pass *stage_lookup* to avoid an extra API round-trip.

        Returns the number of candidates synced.
        """
        # Guard: skip inactive jobs
        job_state = frappe.db.get_value("Workable Job", shortcode, "state") or ""
        if job_state in _INACTIVE_JOB_STATES:
            print(f"[WorkableSync] Skipping candidates for {shortcode} (job state={job_state})")
            return 0

        if stage_lookup is None:
            stages = self.workable_client.list_stages()
            stage_lookup = {s["name"]: s["slug"] for s in stages}

        candidates = self.workable_client.list_job_candidates(
            shortcode, updated_after=updated_after, paginate=True
        )

        job_rows = []
        for candidate in candidates:
            self.repo.workable_candidate.create_or_update(
                self.adapter.workable.candidate_to_db(candidate, stage_lookup)
            )
            job_rows.append(
                self.adapter.workable.candidate_to_job_row(candidate, stage_lookup)
            )

        # Rebuild the job's candidates child table only when there is new data.
        # Each create_or_update above already committed individually, so a
        # mid-loop crash leaves all completed candidate records intact.
        if job_rows:
            self.repo.workable_job.create_or_update(
                cast(WorkableJobDBModel, {"name": shortcode, "candidates": job_rows})
            )

        return len(candidates)

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def sync_events(
        self,
        *,
        event_type: str = "interview",
        include_cancelled: bool = False,
        since_id: str | None = None,
        paginate: bool = False,
    ) -> int:
        """
        Fetch calendar events from Workable and upsert into Frappe.

        Pass *since_id* to fetch only events newer than that cursor (the
        Workable events API has no timestamp filter, so we use the max
        event ID stored locally).  If omitted, a full fetch is performed —
        only do that on the very first sync.

        Events whose ``ends_at`` is already in the past are skipped to
        avoid accumulating stale data.

        Returns the number of events synced.
        """
        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        events = self.workable_client.list_events(
            event_type=event_type,
            include_cancelled=include_cancelled,
            since_id=since_id,
            paginate=paginate,
        )

        synced = 0
        skipped_ended = 0
        for event in events:
            ends_at_raw = event.get("ends_at") or ""
            # Normalise "2024-06-01T14:00:00Z" → "2024-06-01 14:00:00"
            ends_at = ends_at_raw.replace("T", " ").replace("Z", "").split(".")[0]
            if ends_at and ends_at < now_str:
                skipped_ended += 1
                continue
            self.repo.workable_event.create_or_update(
                self.adapter.workable.event_to_db(event)
            )
            synced += 1

        print(f"[WorkableSync] events: synced={synced} skipped_ended={skipped_ended}")
        return synced

    # ------------------------------------------------------------------
    # Full sync
    # ------------------------------------------------------------------

    def sync_all(
        self,
        *,
        state: WorkableJobState = "published",
        updated_after: str | None = None,
    ) -> dict[str, int]:
        """
        Event-centric ETL — driven by future interview events:

          1. Fetch pipeline stages (needed for candidate stage slug mapping).
          2. Fetch interview events from Workable using a cursor (since_id =
             max event ID already in DB) so only new events are pulled.
             Filter to future-only (ends_at > now).
          3. For each future event:
             a. Ensure the linked job exists in Workable Job — fetch + insert if not.
             b. Ensure the linked candidate exists in Workable Candidate — fetch + insert if not.
             c. Ensure the candidate row is present in the job's candidates child table.
             d. Upsert the event itself.
          4. Move to the next event.

        Every record is committed individually so a crash mid-run leaves all
        completed records intact — nothing is rolled back.
        """
        def _log(msg: str) -> None:
            print(msg)

        now_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        
        from datetime import timedelta
        yesterday = datetime.now(timezone.utc) - timedelta(days=1)
        start_iso = yesterday.strftime("%Y-%m-%dT%H:%M:%S.000Z")
        start_str = yesterday.strftime("%Y-%m-%d %H:%M:%S")
        
        _log(f"sync_all started  now={now_str}  fetching from={start_iso}")

        # ── Step 1: Stages ───────────────────────────────────────────
        _log("[1] fetching pipeline stages...")
        stage_lookup = self.sync_stages()
        _log(f"[1] done — {len(stage_lookup)} stages: {list(stage_lookup.keys())}")

        # ── Step 2: Fetch recent/future events ─────────────────────────
        # We pass start_date = yesterday to get events happening from 24h ago onwards
        paginate = True
        _log(f"[2] fetching events (24h window)...")
        try:
            raw_events = self.workable_client.list_events(
                event_type="interview",
                include_cancelled=False,
                since_id=None,
                paginate=paginate,
                start_date=start_iso,
            )
        except Exception as exc:
            _log(f"[2] event fetch failed: {exc} — aborting")
            raise

        future_events = [
            ev for ev in raw_events
            if (ev.get("ends_at") or "").replace("T", " ").replace("Z", "").split(".")[0] > start_str
        ]
        _log(
            f"[2] done — {len(raw_events)} total events fetched from Workable via start_date filter, "
            f"{len(future_events)} passed the local ends_at > {start_str} check"
        )

        # ── Steps 3a-d: Per-event processing ────────────────────────
        synced_events = 0
        failed_events = 0

        for idx, event in enumerate(future_events, 1):
            event_id  = event.get("id") or ""
            shortcode = (event.get("job")       or {}).get("shortcode") or ""
            cand_id   = (event.get("candidate") or {}).get("id")        or ""
            starts_at = event.get("starts_at", "")
            _log(
                f"\n[event {idx}/{len(future_events)}] "
                f"id={event_id}  job={shortcode}  candidate={cand_id}  starts={starts_at}"
            )

            try:
                # ── 3a: Job ──────────────────────────────────────────
                _log(f"  [3a] checking job {shortcode!r}...")
                if shortcode and not frappe.db.exists("Workable Job", shortcode):
                    _log(f"  [3a] not found — fetching job {shortcode} from Workable")
                    job_data  = self.workable_client.get_job(shortcode)
                    stage_list = self.workable_client.list_stages()
                    self.repo.workable_job.create_or_update(
                        self.adapter.workable.job_to_db(job_data, stage_list)
                    )
                    _log(f"  [3a] job {shortcode} inserted")
                else:
                    _log(f"  [3a] job {shortcode} already exists — skipping")

                # ── 3b: Candidate ────────────────────────────────────
                _log(f"  [3b] checking candidate {cand_id!r}...")
                if cand_id and not frappe.db.exists("Workable Candidate", cand_id):
                    _log(f"  [3b] not found — fetching candidate {cand_id} from Workable")
                    cand_data = self.workable_client.get_candidate(shortcode, cand_id)
                    self.repo.workable_candidate.create_or_update(
                        self.adapter.workable.candidate_to_db(cand_data, stage_lookup)
                    )
                    _log(f"  [3b] candidate {cand_id} inserted")
                else:
                    _log(f"  [3b] candidate {cand_id} already exists — skipping")

                # ── 3c: Candidate → Job link ─────────────────────────
                if shortcode and cand_id:
                    _log(f"  [3c] checking candidate-job link {cand_id} → {shortcode}...")
                    already_linked = frappe.db.get_value(
                        "Workable Job Candidate",
                        {"parent": shortcode, "candidate": cand_id},
                        "name",
                    )
                    if not already_linked:
                        _log(f"  [3c] link missing — adding candidate to job")
                        cand_stage = frappe.db.get_value(
                            "Workable Candidate", cand_id, "stage"
                        ) or ""
                        job_doc = frappe.get_doc("Workable Job", shortcode)
                        job_doc.append("candidates", {
                            "name": frappe.generate_hash(length=10),
                            "candidate": cand_id,
                            "stage":     cand_stage,
                            "disqualified": 0,
                            "hired_at": None,
                        })
                        job_doc.save(ignore_permissions=True)
                        frappe.db.commit()
                        _log(f"  [3c] link added  stage={cand_stage!r}")
                    else:
                        _log(f"  [3c] already linked — skipping")

                # ── 3d: Event ────────────────────────────────────────
                _log(f"  [3d] saving event {event_id}...")
                self.repo.workable_event.create_or_update(
                    self.adapter.workable.event_to_db(event)
                )
                
                # Commit the entire transaction for this event
                frappe.db.commit()
                _log(f"  [3d] event {event_id} saved and committed")
                synced_events += 1

            except Exception as exc:
                _log(f"  ERROR on event {event_id}: {exc}")
                frappe.db.rollback()
                failed_events += 1

        summary: dict[str, Any] = {
            "stages":         len(stage_lookup),
            "events_fetched": len(raw_events),
            "events_future":  len(future_events),
            "events_synced":  synced_events,
            "events_failed":  failed_events,
        }
        _log(f"\nsync_all done: {summary}")
        return summary

