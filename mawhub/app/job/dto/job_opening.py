from datetime import date, datetime
import json
from typing import List, Mapping, TypeVar, TypedDict, cast
from frappe import Any, Optional
from frappe.utils import secho

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
    parsed_documents:List
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


T = TypeVar("T")

def get(
    row: Mapping[str, Any],
    key: str,
    default: T,
) -> T:
    value = row.get(key, default)
    return cast(T, value)
def job_opening_sql_to_dto(job: JobView) -> JobOpeningDTO:
    # ---------------------------
    # Parse steps
    # ---------------------------
    steps_raw = get(job, "steps", [])
    if isinstance(steps_raw, str):
        try:
            steps = json.loads(steps_raw)
        except json.JSONDecodeError as exc:
            raise ValueError("Invalid JSON in job.steps") from exc
    else:
        steps = []

    steps = cast(list[JobPipelineStepDTO], steps)

    parsed_documents  : str = cast(str,get(job, "parsed_documents", "[]"))
    dto: JobOpeningDTO = {
        "name": get(job, "name", ""),
        "designation": get(job, "designation", ""),
        "department": get(job, "department", ""),
        "parsed_documents": json.loads(parsed_documents),
        "employment_type": get(job, "employment_type", ""),
        "location": get(job, "location", ""),

        "docstatus": get(job, "docstatus", 1),

        "publish": get(job, "publish", True),
        "publish_salary_range": get(job, "publish_salary_range", False),
        "publish_applications_received": get(job, "publish_applications_received", False),

        "route": get(job, "route", ""),
        "job_application_route": get(job, "job_application_route", ""),

        "currency": get(job, "currency", ""),
        "salary_per": get(job, "salary_per", ""),
        "lower_range": str(get(job, "lower_range", 0)),
        "upper_range": str(get(job, "upper_range", 0)),

        "posted_on": _dt_to_str(job.get("posted_on")),
        "closes_on": _dt_to_str(job.get("closes_on")),

        "step_count": get(job, "step_count", 0),
        "candidate_count": get(job, "candidate_count", 0),

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
