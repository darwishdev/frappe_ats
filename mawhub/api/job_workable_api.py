import frappe
from mawhub.bootstrap import app_container
from mawhub.app.job.usecase.job_workable_usecase import JobWorkableUsecase


@frappe.whitelist(methods=["POST"], allow_guest=True)
def workable_sync_stages():
    """
    Fetch all pipeline stages from Workable and upsert into Frappe.
    Fast — runs synchronously and returns the stage slug list.
    """
    stage_lookup = app_container.job_usecase.workable.sync_stages()
    return {"stages": list(stage_lookup.keys())}


@frappe.whitelist(methods=["POST"], allow_guest=True)
def workable_sync_jobs(state: str = "published", updated_after: str | None = None):
    """
    Fetch jobs from Workable and upsert into Frappe.
    Enqueued as a background job — returns immediately with the queue key.

    Args:
        state:         Job state filter (draft | published | archived | closed).
        updated_after: ISO-8601 datetime — only sync jobs updated after this
                       timestamp (useful for incremental runs).
    """
    shortcodes = app_container.job_usecase.workable.sync_jobs(
        state=state,  # type: ignore[arg-type]
        updated_after=updated_after or None,
        paginate=True,
    )
    return {"status": "done", "jobs": len(shortcodes), "shortcodes": shortcodes}


@frappe.whitelist(methods=["POST"], allow_guest=True)
def workable_sync_candidates(shortcode: str, updated_after: str | None = None):
    """
    Fetch every candidate for *shortcode* and upsert into Frappe.
    Enqueued as a background job — returns immediately with the queue key.

    Args:
        shortcode:     Workable job shortcode (e.g. "EA389D5257").
        updated_after: Only sync candidates updated after this timestamp.
    """
    count = app_container.job_usecase.workable.sync_candidates_for_job(
        shortcode, updated_after=updated_after or None, stage_lookup=None
    )
    return {"status": "done", "shortcode": shortcode, "candidates": count}


@frappe.whitelist(methods=["POST"], allow_guest=True)
def workable_sync_events(
    event_type: str = "interview",
    include_cancelled: bool = False,
    since_id: str | None = None,
):
    """
    Fetch calendar events from Workable and upsert into Frappe.
    Runs synchronously and returns the count of events synced.

    Omit *since_id* to use the auto-detected cursor (MAX event ID in Frappe).
    Pass ``since_id=""`` to force a full first-page fetch from the beginning.

    Args:
        event_type:        Event type filter (default: "interview").
        include_cancelled: Include cancelled events (default: False).
        since_id:          Workable cursor ID for incremental fetches.
    """
    resolved_since_id = since_id if since_id is not None else JobWorkableUsecase._last_event_since_id()  # type: ignore[misc]
    paginate = resolved_since_id is not None
    count = app_container.job_usecase.workable.sync_events(
        event_type=event_type,
        include_cancelled=bool(include_cancelled),
        since_id=resolved_since_id,
        paginate=paginate,
    )
    return {"status": "done", "events": count}


@frappe.whitelist(methods=["POST"], allow_guest=True)
def workable_sync_all(state: str = "published", updated_after: str | None = None):
    """
    Full ETL in dependency order: stages → events → jobs/candidates/links.
    Runs synchronously for debugging/foreground use.

    Args:
        state:         Job state filter (draft | published | archived | closed).
        updated_after: ISO-8601 datetime string for incremental sync.
    """
    summary = app_container.job_usecase.workable.sync_all(
        state=state,  # type: ignore[arg-type]
        updated_after=updated_after or None,
    )
    return {"status": "done", **summary}


@frappe.whitelist(methods=["POST"], allow_guest=True)
def sync_workable_to_native():
    """
    Bridge Layer 2: copy already-synced Workable DocType data into native
    Frappe HRMS ATS records (Job Opening, Job Applicant, Interview).

    Run workable_sync_all first to populate the Workable DocTypes,
    then call this endpoint to mirror the data into the native ATS.

    Returns a summary: {"jobs": N, "candidates": N, "interviews": N}
    """
    summary = app_container.job_usecase.native_sync.sync_all_native()
    return {"status": "done", **summary}
