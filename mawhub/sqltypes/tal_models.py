# AUTO-GENERATED FILE
# Source: MariaDB information_schema
# Contains TypedDicts for $tal_* tables
# Do not edit manually

from typing import TypedDict, NotRequired
from datetime import date, datetime

class JobApplicantsView(TypedDict):
    job_opening_id: str
    pipeline_id: str
    pipeline_description: NotRequired[str]
    pipeline_is_primary: int
    pipeline_docstatus: int
    pipeline_created_at: NotRequired[datetime]
    pipeline_modified_at: NotRequired[datetime]
    pipeline_step_id: str
    pipeline_step_idx: int
    pipeline_step_name: NotRequired[str]
    pipeline_step_type: NotRequired[str]
    pipeline_parent_id: NotRequired[str]
    applicant_id: str
    applicant_name: NotRequired[str]
    applicant_email: NotRequired[str]
    applicant_phone: NotRequired[str]
    applicant_country: NotRequired[str]
    applicant_job_title: NotRequired[str]
    applicant_designation: NotRequired[str]
    applicant_status: NotRequired[str]
    applicant_source: NotRequired[str]
    applicant_source_name: NotRequired[str]
    applicant_employee_referral: NotRequired[str]
    applicant_rating: NotRequired[float]
    applicant_resume_link: NotRequired[str]
    applicant_resume_attachment: NotRequired[str]
    applicant_cover_letter: NotRequired[str]
    applicant_pipeline_step_ref: NotRequired[str]
    applicant_docstatus: int
    applicant_created_at: NotRequired[datetime]
    applicant_modified_at: NotRequired[datetime]
    appointment_letters: NotRequired[str]
    job_offers: NotRequired[str]
    interviews: NotRequired[str]

class JobView(TypedDict):
    name: str
    designation: NotRequired[str]
    department: NotRequired[str]
    employment_type: NotRequired[str]
    location: NotRequired[str]
    docstatus: NotRequired[int]
    publish_salary_range: int
    currency: NotRequired[str]
    lower_range: float
    upper_range: float
    posted_on: NotRequired[datetime]
    closes_on: NotRequired[date]
    step_count: int
    total_candidate_count: float
    steps: NotRequired[str]
    parsed_documents: str

class ParsedDocumentView(TypedDict):
    document_id: str
    file: NotRequired[str]
    file_hash: NotRequired[str]
    parent_type: NotRequired[str]
    parent_id: NotRequired[str]
    meta_data: NotRequired[str]
    creation: NotRequired[datetime]
    sections: NotRequired[str]
