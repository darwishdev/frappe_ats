from typing import Protocol

from mawhub.app.applicant.repo.job_applicant_repo import JobApplicantDBModel
from mawhub.app.interview.repo.interview_interview_repo import InterviewDBModel
from mawhub.app.job.repo.job_opening_repo import JobOpeningDBModel


class JobWorkableNativeAdapterInterface(Protocol):
    def workable_job_to_opening(self, wj: dict) -> JobOpeningDBModel: ...
    def workable_candidate_to_applicant(
        self,
        candidate: dict,
        job_candidate_row: dict,
        job_opening_name: str,
    ) -> JobApplicantDBModel: ...
    def workable_event_to_interview(
        self,
        event: dict,
        job_applicant_name: str,
        job_opening_name: str,
        interview_round_name: str,
    ) -> InterviewDBModel: ...


class JobWorkableNativeAdapter:

    def workable_job_to_opening(self, wj: dict) -> JobOpeningDBModel:
        state = wj.get("state") or ""
        status = "Open" if state == "published" else "Closed"

        description_parts = [
            p for p in [
                wj.get("description"),
                wj.get("full_description"),
                wj.get("requirements"),
                wj.get("benefits"),
            ] if p
        ]
        description = "\n\n".join(description_parts)

        location_label = wj.get("city") or wj.get("country") or ""

        return JobOpeningDBModel(
            custom_workable_shortcode=wj["name"],
            job_title=wj.get("title") or "",
            designation=wj.get("title") or "",
            company="Mawhub",
            status=status,
            department=wj.get("department") or "",
            employment_type=wj.get("employment_type") or "",
            location=location_label,
            currency=wj.get("salary_currency") or "",
            description=description,
            publish=0,
            publish_applications_received=0,
            salary_per="Month",
            publish_salary_range=0,
        )

    def workable_candidate_to_applicant(
        self,
        candidate: dict,
        job_candidate_row: dict,
        job_opening_name: str,
    ) -> JobApplicantDBModel:
        if candidate.get("disqualified"):
            status = "Rejected"
        elif candidate.get("hired_at"):
            status = "Accepted"
        else:
            status = "Open"

        first = candidate.get("firstname") or ""
        last = candidate.get("lastname") or ""
        full_name = f"{first} {last}".strip() or candidate.get("email") or "Unknown"

        return JobApplicantDBModel(
            custom_workable_candidate_id=candidate["name"],
            custom_workable_shortcode=job_candidate_row.get("parent") or "",
            applicant_name=full_name,
            email_id=candidate.get("email") or "",
            phone_number=candidate.get("phone") or "",
            country=candidate.get("country") or "",
            job_title=job_opening_name,
            cover_letter=candidate.get("cover_letter") or "",
            # Workable resume_url is a pre-signed S3 link (~200 chars, expires in
            # hours). Job Applicant.resume_link is a Small Text field (max 140
            # chars) so we leave it blank — the URL is available on
            # Workable Candidate.resume_url if needed.
            resume_link="",
            status=status,
            applicant_rating=None,
            lower_range=None,
            upper_range=None,
        )

    def workable_event_to_interview(
        self,
        event: dict,
        job_applicant_name: str,
        job_opening_name: str,
        interview_round_name: str,
    ) -> InterviewDBModel:
        starts_at = event.get("starts_at") or ""  # "YYYY-MM-DD HH:MM:SS"
        ends_at = event.get("ends_at") or ""

        scheduled_on = starts_at[:10] if starts_at else ""
        from_time = starts_at[11:] if len(starts_at) > 10 else ""
        to_time = ends_at[11:] if len(ends_at) > 10 else ""

        status = "Cancelled" if event.get("cancelled") else "Pending"

        return InterviewDBModel(
            custom_workable_event_id=event["name"],
            interview_round=interview_round_name,
            job_applicant=job_applicant_name,
            custom_job_opening=job_opening_name,
            status=status,
            scheduled_on=scheduled_on,
            from_time=from_time,
            to_time=to_time,
            average_rating=None,
            expected_average_rating=None,
        )
