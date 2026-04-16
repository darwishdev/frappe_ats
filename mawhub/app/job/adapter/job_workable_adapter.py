import json
from typing import Optional


def _dt(value: Optional[str]) -> Optional[str]:
    """Convert an ISO-8601 datetime string to the MySQL-compatible format
    that Frappe Datetime fields expect (``YYYY-MM-DD HH:MM:SS``).

    Handles the two common Workable formats:
      - ``2021-09-20T17:45:29Z``
      - ``2021-09-20T17:45:29.123Z``

    Returns *None* for falsy inputs so optional Datetime fields stay NULL.
    """
    if not value:
        return None
    return value.replace("T", " ").replace("Z", "").split(".")[0]


from mawhub.mawhub.doctype.workable_candidate.workable_candidate import WorkableCandidateDBModel
from mawhub.mawhub.doctype.workable_job.workable_job import WorkableJobDBModel
from mawhub.mawhub.doctype.workable_job_candidate.workable_job_candidate import WorkableJobCandidateDBModel
from mawhub.mawhub.doctype.workable_job_stage.workable_job_stage import WorkableJobStageDBModel
from mawhub.mawhub.doctype.workable_stage.workable_stage import WorkableStageDBModel
from mawhub.mawhub.doctype.workable_event.workable_event import WorkableEventDBModel
from mawhub.pkg.workable.workable_types import WorkableCandidate, WorkableEvent, WorkableJob, WorkableStage


class JobWorkableAdapter:

    def stage_to_db(self, stage: WorkableStage) -> WorkableStageDBModel:
        return WorkableStageDBModel(
            name=stage["slug"],
            stage_name=stage["name"],
            kind=stage["kind"],
            position=stage["position"],
        )

    def job_stage_row(self, stage: WorkableStage) -> WorkableJobStageDBModel:
        return WorkableJobStageDBModel(stage=stage["slug"])

    def candidate_to_db(
        self,
        candidate: WorkableCandidate,
        stage_lookup: dict[str, str],
    ) -> WorkableCandidateDBModel:
        loc = candidate.get("location") or {}
        resume_meta = candidate.get("resume_metadata") or {}

        linkedin_url = ""
        for sp in candidate.get("social_profiles") or []:
            if sp.get("type") == "linkedin":
                linkedin_url = sp.get("url") or ""
                break

        stage_slug = stage_lookup.get(candidate.get("stage") or "", "")

        return WorkableCandidateDBModel(
            name=candidate["id"],
            firstname=candidate.get("firstname") or "",
            lastname=candidate.get("lastname") or "",
            email=candidate.get("email") or "",
            phone=candidate.get("phone") or "",
            headline=candidate.get("headline") or "",
            address=candidate.get("address") or "",
            country=loc.get("country") or "",
            country_code=loc.get("country_code") or "",
            city=loc.get("city") or "",
            region=loc.get("region") or "",
            stage=stage_slug,
            stage_kind=candidate.get("stage_kind") or "",
            disqualified=1 if candidate.get("disqualified") else 0,
            disqualified_at=_dt(candidate.get("disqualified_at")),
            disqualification_reason=candidate.get("disqualification_reason") or "",
            withdrew=1 if candidate.get("withdrew") else 0,
            hired_at=_dt(candidate.get("hired_at")),
            moved_to_offer_at=_dt(candidate.get("moved_to_offer_at")),
            sourced=1 if candidate.get("sourced") else 0,
            domain=candidate.get("domain") or "",
            outlet=candidate.get("outlet") or "",
            common_source=candidate.get("common_source") or "",
            common_source_category=candidate.get("common_source_category") or "",
            profile_url=candidate.get("profile_url") or "",
            resume_url=candidate.get("resume_url") or "",
            resume_filename=resume_meta.get("filename") or "",
            linkedin_url=linkedin_url,
            cover_letter=candidate.get("cover_letter") or "",
            summary=candidate.get("summary") or "",
            education_entries=json.dumps(
                candidate.get("education_entries") or [], ensure_ascii=False
            ),
            experience_entries=json.dumps(
                candidate.get("experience_entries") or [], ensure_ascii=False
            ),
            skills=json.dumps(candidate.get("skills") or [], ensure_ascii=False),
            workable_created_at=_dt(candidate.get("created_at")) or "",
            workable_updated_at=_dt(candidate.get("updated_at")) or "",
        )

    def candidate_to_job_row(
        self,
        candidate: WorkableCandidate,
        stage_lookup: dict[str, str],
    ) -> WorkableJobCandidateDBModel:
        stage_slug = stage_lookup.get(candidate.get("stage") or "", "")
        return WorkableJobCandidateDBModel(
            candidate=candidate["id"],
            stage=stage_slug,
            disqualified=1 if candidate.get("disqualified") else 0,
            hired_at=_dt(candidate.get("hired_at")),
        )

    def event_to_db(self, event: WorkableEvent) -> WorkableEventDBModel:
        members = event.get("members") or []
        return WorkableEventDBModel(
            name=event["id"],
            title=event.get("title") or "",
            event_type=event.get("type") or "",
            cancelled=1 if event.get("cancelled") else 0,
            starts_at=_dt(event.get("starts_at")),
            ends_at=_dt(event.get("ends_at")),
            conference_type=(event.get("conference") or {}).get("type") or "",
            conference_url=(event.get("conference") or {}).get("link") or "",
            job=(event.get("job") or {}).get("shortcode") or "",
            job_title=(event.get("job") or {}).get("title") or "",
            candidate=(event.get("candidate") or {}).get("id") or "",
            candidate_name=(event.get("candidate") or {}).get("name") or "",
            description=event.get("description") or "",
            members=json.dumps(members, ensure_ascii=False),
        )

    def job_to_db(
        self,
        job: WorkableJob,
        stages: list[WorkableStage],
    ) -> WorkableJobDBModel:
        loc = job.get("location") or {}
        salary = job.get("salary") or {}

        return WorkableJobDBModel(
            name=job["shortcode"],
            workable_id=job.get("id") or "",
            title=job["title"],
            state=job.get("state") or "draft",
            confidential=1 if job.get("confidential") else 0,
            full_title=job.get("full_title") or "",
            code=job.get("code") or "",
            department=job.get("department") or "",
            workplace_type=job.get("workplace_type") or "",
            employment_type=job.get("employment_type") or "",
            industry=job.get("industry") or "",
            job_function=job.get("function") or "",
            experience=job.get("experience") or "",
            education=job.get("education") or "",
            country=loc.get("country") or "",
            country_code=loc.get("country_code") or "",
            city=loc.get("city") or "",
            region=loc.get("region") or "",
            salary_currency=salary.get("salary_currency") or "",
            url=job.get("url") or "",
            application_url=job.get("application_url") or "",
            shortlink=job.get("shortlink") or "",
            keywords=", ".join(job.get("keywords") or []),
            description=job.get("description") or "",
            full_description=job.get("full_description") or "",
            requirements=job.get("requirements") or "",
            benefits=job.get("benefits") or "",
            stages=[self.job_stage_row(s) for s in stages],
            workable_created_at=_dt(job.get("created_at")) or "",
            workable_updated_at=_dt(job.get("updated_at")) or "",
        )
