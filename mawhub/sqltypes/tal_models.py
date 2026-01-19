# AUTO-GENERATED FILE
# Source: MariaDB information_schema
# Contains TypedDicts for $tal_* tables
# Do not edit manually

from typing import TypedDict, Optional
from datetime import date, datetime

class JobApplicantsView(TypedDict):
    job_opening_id: str
    pipeline_id: str
    pipeline_description: Optional[str]
    pipeline_is_primary: int
    pipeline_docstatus: int
    pipeline_created_at: Optional[datetime]
    pipeline_modified_at: Optional[datetime]
    pipeline_step_id: int
    pipeline_step_idx: int
    pipeline_step_name: Optional[str]
    pipeline_step_type: Optional[str]
    pipeline_parent_id: Optional[str]
    applicant_id: str
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
    applicant_docstatus: int
    applicant_created_at: Optional[datetime]
    applicant_modified_at: Optional[datetime]
    appointment_letters: Optional[str]
    job_offers: Optional[str]
    interviews: Optional[str]

class JobView(TypedDict):
    name: str
    designation: Optional[str]
    department: Optional[str]
    employment_type: Optional[str]
    location: Optional[str]
    docstatus: int
    publish_salary_range: int
    publish_applications_received: int
    publish: int
    route: Optional[str]
    job_application_route: Optional[str]
    currency: Optional[str]
    salary_per: Optional[str]
    lower_range: float
    upper_range: float
    posted_on: Optional[datetime]
    closes_on: Optional[date]
    step_count: int
    candidate_count: int
    steps: Optional[str]
