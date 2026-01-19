from datetime import date, datetime
import json
from typing import List, TypedDict, cast
from frappe import Optional

from mawhub.sqltypes.tal_models import JobView

class InterviewFeedbackDTO(TypedDict):
    feedback_id: str
    feedback_interviewer: str
    feedback_result: str
    feedback_average_rating: float
    feedback_text: Optional[str]
    feedback_docstatus: int
    feedback_created_at: str
    feedback_modified_at: str

class InterviewDTO(TypedDict):
    interview_id: str
    interview_round: str
    interview_status: str
    interview_scheduled_on: str
    interview_from_time: str
    interview_to_time: str
    interview_expected_avg_rating: float
    interview_average_rating: float
    interview_job_opening: str
    interview_designation: str
    interview_docstatus: int
    interview_created_at: str
    interview_modified_at: str
    feedbacks: List[InterviewFeedbackDTO]

class AppointmentLetterDTO(TypedDict):
    appointment_letter_id: str
    appointment_company: str
    appointment_date: str
    appointment_template: str
    appointment_docstatus: int
    appointment_created_at: str
    appointment_modified_at: str

class JobOfferDTO(TypedDict):
    job_offer_id: str
    job_offer_status: str
    job_offer_date: str
    job_offer_company: str
    job_offer_designation: str
    job_offer_applicant_email: str
    job_offer_docstatus: int
    job_offer_created_at: str
    job_offer_modified_at: str
class CandidateDTO(TypedDict):
    # Job / Pipeline context
    job_opening_id: Optional[str]
    pipeline_id: Optional[str]
    pipeline_description: Optional[str]
    pipeline_is_primary: Optional[int]
    pipeline_docstatus: Optional[int]
    pipeline_created_at: Optional[str]
    pipeline_modified_at: Optional[str]

    pipeline_step_id: Optional[int]
    pipeline_step_idx: Optional[int]
    pipeline_step_name: Optional[str]
    pipeline_step_type: Optional[str]
    pipeline_parent_id: Optional[str]

    # Applicant info
    applicant_id: Optional[str]
    applicant_name: Optional[str]
    applicant_email: Optional[str]
    applicant_phone: Optional[str]
    applicant_country: Optional[str]
    applicant_job_title: Optional[str]
    applicant_designation: Optional[str]
    applicant_status: Optional[str]
    applicant_source: Optional[str]
    applicant_source_name: Optional[str]
    applicant_employee_referral: Optional[str]
    applicant_rating: Optional[float]

    applicant_resume_link: Optional[str]
    applicant_resume_attachment: Optional[str]
    applicant_cover_letter: Optional[str]

    applicant_pipeline_step_ref: Optional[str]
    applicant_docstatus: Optional[int]
    applicant_created_at: Optional[str]
    applicant_modified_at: Optional[str]

    # Nested HR objects
    appointment_letters: Optional[List[AppointmentLetterDTO]]
    job_offers: Optional[List[JobOfferDTO]]
    interviews: Optional[List[InterviewDTO]]
class JobPipelineStepDTO(TypedDict):
    step_id: int
    step_name: str
    step_type: str
    step_idx: int
    candidates: List[CandidateDTO]
    candidate_count: int
class JobOpeningDTO(TypedDict):
    name: str
    designation: str
    department: Optional[str]
    employment_type: str
    location: str

    docstatus: int
    publish: int
    publish_salary_range: int
    publish_applications_received: int

    route: str
    job_application_route: Optional[str]

    currency: str
    salary_per: str
    lower_range: str
    upper_range: str

    posted_on: str
    closes_on: str

    step_count: int
    candidate_count: int

    steps: List[JobPipelineStepDTO]


def _dt_to_str(value: date | datetime | None) -> str:
    if value is None:
        return ""
    return value.isoformat()

def job_opening_sql_to_dto(job: JobView) -> JobOpeningDTO:
    """
    Convert DB JobView into API JobOpeningDTO
    """

    # --------------------------------------------------
    # Parse steps JSON
    # --------------------------------------------------
    if isinstance(job["steps"] , str):
        try:
            steps = json.loads(job["steps"])
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON in job.steps") from exc
    else:
        steps = []

    # Optional: validate shape if you want stricter guarantees
    steps = cast(list[JobPipelineStepDTO], steps)

    # --------------------------------------------------
    # Build DTO
    # --------------------------------------------------
    dto: JobOpeningDTO = {
        "name": job["name"],
        "designation": job.get("designation") or "",
        "department": job.get("department"),
        "employment_type": job.get("employment_type") or "",
        "location": job.get("location") or "",

        "docstatus": job["docstatus"],
        "publish": job["publish"],
        "publish_salary_range": job["publish_salary_range"],
        "publish_applications_received": job["publish_applications_received"],

        "route": job.get("route") or "",
        "job_application_route": job.get("job_application_route"),

        "currency": job.get("currency") or "",
        "salary_per": job.get("salary_per") or "",
        "lower_range": str(job["lower_range"]),
        "upper_range": str(job["upper_range"]),

        "posted_on": _dt_to_str(job.get("posted_on")),
        "closes_on": _dt_to_str(job.get("closes_on")),

        "step_count": job["step_count"],
        "candidate_count": job["candidate_count"],

        "steps": steps,
    }

    return dto


def job_opening_list_sql_to_dto(
    jobs: List[JobView] | None,
) -> List[JobOpeningDTO]:
    """
    Convert a list of DB JobView rows into JobOpeningDTOs.
    """
    if not jobs:
        return []

    result: List[JobOpeningDTO] = []
    for job in jobs:
        result.append(job_opening_sql_to_dto(job))

    return result
