from typing import List, TypedDict

from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO

class JobApplicantCreateWithResume(TypedDict):
    applicant_resume: ApplicantResumeDTO
    pipeline_step_id: str
    job_opening_id: str

class JobApplicantUpdateRequest(TypedDict):
    name: str
    status: str
    pipeline_step: str

class JobApplicantBulkUpdateRequest(TypedDict):
    names: List[str]
    status: str
    pipeline_step: str

