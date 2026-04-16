from typing import Any, Protocol

import frappe

from mawhub.app.applicant.repo.applicant_repo import ApplicantRepoInterface
from mawhub.app.interview.repo.interview_repo import InterviewRepoInterface
from mawhub.app.job.adapter.job_adapter import JobAdapterInterface
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.app.job.usecase.job_opening_usecase import JobOpeningUsecaseInterface


class JobWorkableNativeSyncUsecaseInterface(Protocol):
    def sync_jobs_to_openings(self) -> int: ...
    def sync_candidates_to_applicants(self) -> int: ...
    def sync_events_to_interviews(self) -> int: ...
    def sync_all_native(self) -> dict[str, Any]: ...


class JobWorkableNativeSyncUsecase:
    repo: JobRepoInterface
    applicant_repo: ApplicantRepoInterface
    interview_repo: InterviewRepoInterface
    adapter: JobAdapterInterface
    job_opening_usecase: JobOpeningUsecaseInterface

    def __init__(
        self,
        repo: JobRepoInterface,
        applicant_repo: ApplicantRepoInterface,
        interview_repo: InterviewRepoInterface,
        adapter: JobAdapterInterface,
        job_opening_usecase: JobOpeningUsecaseInterface,
    ):
        self.repo = repo
        self.applicant_repo = applicant_repo
        self.interview_repo = interview_repo
        self.adapter = adapter
        self.job_opening_usecase = job_opening_usecase

    # ------------------------------------------------------------------
    # Jobs → Job Openings
    # ------------------------------------------------------------------

    def sync_jobs_to_openings(self) -> int:
        """
        Read every Workable Job and upsert into native Job Opening.
        Idempotent: looks up existing records by custom_workable_shortcode.
        """
        workable_jobs = frappe.get_all(
            "Workable Job",
            fields=[
                "name", "title", "state", "department", "employment_type",
                "city", "country", "salary_currency",
                "description", "full_description", "requirements", "benefits",
            ],
        )

        synced = 0
        for wj in workable_jobs:
            try:
                designation_name = self.job_opening_usecase.ensure_designation(
                    wj.get("title") or ""
                )

                location_label = wj.get("city") or wj.get("country") or ""
                location_name = (
                    self.job_opening_usecase.ensure_location(location_label)
                    if location_label else ""
                )

                department_name = ""
                if wj.get("department"):
                    department_name = self.job_opening_usecase.ensure_department(
                        wj["department"]
                    )

                payload = self.adapter.native.workable_job_to_opening(wj)
                payload["designation"] = designation_name
                if location_name:
                    payload["location"] = location_name
                if department_name:
                    payload["department"] = department_name

                existing = frappe.db.get_value(
                    "Job Opening",
                    {"custom_workable_shortcode": wj["name"]},
                    "name",
                )
                # Always set an explicit name so Frappe never falls back to the
                # naming series (which causes duplicates across jobs).
                # Existing record → keep its name.  New record → use the
                # Workable shortcode as the document name.
                payload["name"] = str(existing) if existing else wj["name"]

                self.repo.job_opening.create_or_update(payload)
                frappe.db.commit()
                synced += 1
            except Exception as exc:
                frappe.db.rollback()
                frappe.log_error(
                    f"[NativeSync] Failed to sync job {wj.get('name')}: {exc}",
                    "WorkableNativeSync.sync_jobs_to_openings",
                )

        print(f"[NativeSync] sync_jobs_to_openings: synced={synced}/{len(workable_jobs)}")
        return synced

    # ------------------------------------------------------------------
    # Candidates → Job Applicants
    # ------------------------------------------------------------------

    def sync_candidates_to_applicants(self) -> int:
        """
        Derive candidate→job pairs from Workable Events (DISTINCT job + candidate)
        so we don't depend on the Workable Job Candidate child table being populated.
        One unique (job, candidate) pair = one Job Applicant.
        """
        pairs: list = frappe.db.sql(
            """
            SELECT DISTINCT we.job AS shortcode, we.candidate AS candidate_id
            FROM `tabWorkable Event` we
            INNER JOIN `tabJob Opening` jo ON jo.custom_workable_shortcode = we.job
            WHERE we.job != '' AND we.job IS NOT NULL
              AND we.candidate != '' AND we.candidate IS NOT NULL
              AND jo.status = 'Open'
            """,
            as_dict=True,
        ) or []

        print(f"[NativeSync] sync_candidates_to_applicants: {len(pairs)} unique event pairs")

        synced = 0
        for pair in pairs:
            shortcode = pair.get("shortcode") or ""
            candidate_id = pair.get("candidate_id") or ""
            if not shortcode or not candidate_id:
                continue

            try:
                job_opening_name = frappe.db.get_value(
                    "Job Opening",
                    {"custom_workable_shortcode": shortcode},
                    "name",
                )
                if not job_opening_name:
                    print(f"[NativeSync] No Job Opening for shortcode {shortcode!r} — skipping candidate {candidate_id}")
                    continue

                candidate = frappe.db.get_value(
                    "Workable Candidate",
                    candidate_id,
                    [
                        "name", "firstname", "lastname", "email", "phone",
                        "country", "cover_letter", "resume_url",
                        "disqualified", "hired_at",
                    ],
                    as_dict=True,
                )
                if not candidate:
                    print(f"[NativeSync] Workable Candidate {candidate_id!r} not found — skipping")
                    continue

                # Build a minimal job_candidate_row with parent so the adapter
                # can store the shortcode on the applicant.
                jc_row = {"parent": shortcode}

                payload = self.adapter.native.workable_candidate_to_applicant(
                    candidate, jc_row, str(job_opening_name)
                )

                existing = frappe.db.get_value(
                    "Job Applicant",
                    {
                        "custom_workable_candidate_id": candidate_id,
                        "job_title": job_opening_name,
                    },
                    "name",
                )
                # Stable composite name bypasses the Job Applicant naming series.
                payload["name"] = str(existing) if existing else f"{shortcode}-{candidate_id}"

                self.applicant_repo.job_applicant.create_or_update(payload)
                frappe.db.commit()
                synced += 1
            except Exception as exc:
                frappe.db.rollback()
                frappe.log_error(
                    f"[NativeSync] Failed to sync candidate {candidate_id} → job {shortcode}: {exc}",
                    "WorkableNativeSync.sync_candidates_to_applicants",
                )

        print(f"[NativeSync] sync_candidates_to_applicants: synced={synced}/{len(pairs)}")
        return synced

    # ------------------------------------------------------------------
    # Events → Interviews
    # ------------------------------------------------------------------

    def sync_events_to_interviews(self) -> int:
        """
        Read every Workable Event and upsert into native Interview.
        Requires the corresponding Job Opening and Job Applicant to exist
        (run sync_jobs_to_openings and sync_candidates_to_applicants first).
        """
        workable_events = frappe.get_all(
            "Workable Event",
            fields=[
                "name", "title", "starts_at", "ends_at", "cancelled",
                "job", "candidate",
            ],
        )

        synced = 0
        for we in workable_events:
            event_id = we.get("name") or ""
            shortcode = we.get("job") or ""
            candidate_id = we.get("candidate") or ""

            if not shortcode or not candidate_id:
                continue

            try:
                job_opening_name = frappe.db.get_value(
                    "Job Opening",
                    {"custom_workable_shortcode": shortcode},
                    "name",
                )
                if not job_opening_name:
                    print(f"[NativeSync] No Job Opening for shortcode {shortcode!r} — skipping event {event_id}")
                    continue

                job_opening_status = frappe.db.get_value("Job Opening", job_opening_name, "status")
                if job_opening_status != "Open":
                    print(f"[NativeSync] Job Opening {job_opening_name} is {job_opening_status!r} — skipping event {event_id}")
                    continue

                job_applicant_name = frappe.db.get_value(
                    "Job Applicant",
                    {
                        "custom_workable_candidate_id": candidate_id,
                        "job_title": job_opening_name,
                    },
                    "name",
                )
                if not job_applicant_name:
                    # Applicant wasn't synced yet — create it now on-the-fly
                    # so the interview can be linked correctly.
                    job_applicant_name = self._ensure_job_applicant(
                        candidate_id, shortcode, str(job_opening_name)
                    )
                if not job_applicant_name:
                    print(f"[NativeSync] Could not find/create Job Applicant for "
                          f"candidate {candidate_id!r} / job {shortcode!r} — skipping event {event_id}")
                    continue

                interview_round_name = self._ensure_interview_round(
                    we.get("title") or "Workable Interview"
                )

                payload = self.adapter.native.workable_event_to_interview(
                    we,
                    str(job_applicant_name),
                    str(job_opening_name),
                    interview_round_name,
                )

                existing = frappe.db.get_value(
                    "Interview",
                    {"custom_workable_event_id": event_id},
                    "name",
                )
                # Use Workable event ID as the document name so it is
                # stable across runs and never hits the naming series.
                payload["name"] = str(existing) if existing else event_id

                self.interview_repo.interview.create_or_update(payload)
                frappe.db.commit()
                synced += 1
            except Exception as exc:
                frappe.db.rollback()
                frappe.log_error(
                    f"[NativeSync] Failed to sync event {event_id}: {exc}",
                    "WorkableNativeSync.sync_events_to_interviews",
                )

        print(f"[NativeSync] sync_events_to_interviews: synced={synced}/{len(workable_events)}")
        return synced

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _ensure_interview_round(self, title: str) -> str:
        """Find or create an Interview Round with the given round_name."""
        existing = frappe.db.get_value("Interview Round", {"round_name": title}, "name")
        if existing:
            return str(existing)
        doc = frappe.new_doc("Interview Round")
        doc.set("round_name", title)
        doc.insert(ignore_permissions=True, ignore_mandatory=True)
        frappe.db.commit()
        return str(doc.name)

    def _ensure_job_applicant(
        self,
        candidate_id: str,
        shortcode: str,
        job_opening_name: str,
    ) -> str | None:
        """
        Fetch the Workable Candidate and create a Job Applicant for it
        on the fly.  Returns the new applicant name, or None on failure.
        """
        candidate = frappe.db.get_value(
            "Workable Candidate",
            candidate_id,
            ["name", "firstname", "lastname", "email", "phone",
             "country", "cover_letter", "resume_url", "disqualified", "hired_at"],
            as_dict=True,
        )
        if not candidate:
            return None

        jc_row = {"parent": shortcode}
        payload = self.adapter.native.workable_candidate_to_applicant(
            candidate, jc_row, job_opening_name
        )
        payload["name"] = f"{shortcode}-{candidate_id}"
        try:
            doc = self.applicant_repo.job_applicant.create_or_update(payload)
            frappe.db.commit()
            return str(doc.name)
        except Exception as exc:
            frappe.db.rollback()
            frappe.log_error(
                f"[NativeSync] Failed to create applicant {candidate_id} for {shortcode}: {exc}",
                "WorkableNativeSync._ensure_job_applicant",
            )
            return None

    # ------------------------------------------------------------------
    # Full sync
    # ------------------------------------------------------------------

    def sync_all_native(self) -> dict[str, Any]:
        """
        Run the full Workable → native ATS bridge in dependency order:
          1. Jobs → Job Openings
          2. Candidates → Job Applicants  (needs job openings to exist)
          3. Events → Interviews           (needs both above to exist)
        """
        print("[NativeSync] Starting sync_all_native...")
        jobs = self.sync_jobs_to_openings()
        candidates = self.sync_candidates_to_applicants()
        interviews = self.sync_events_to_interviews()
        result: dict[str, Any] = {
            "jobs": jobs,
            "candidates": candidates,
            "interviews": interviews,
        }
        print(f"[NativeSync] Done: {result}")
        return result
