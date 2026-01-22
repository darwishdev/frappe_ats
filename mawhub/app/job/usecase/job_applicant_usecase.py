from typing import List, Protocol

from frappe.model.document import Document
from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.app.job.dto.job_applicant import JobApplicantBulkUpdateRequest, JobApplicantCreateWithResume
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.sqltypes.table_models import JobApplicant


class JobApplicantUsecaseInterface(Protocol):
	def job_applicant_create_update(self, payload: JobApplicant)->Document: ...
	def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]: ...
	def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document: ...

class JobApplicantUsecase:
    repo: JobRepoInterface
    def __init__(
        self,
        repo: JobRepoInterface,
    ):
        self.repo = repo

    def job_applicant_create_update(self, payload: JobApplicant)->Document:
        return self.repo.job_applicant.create_or_update(payload)

    def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document:
        applicant_resume = payload.get("applicant_resume")
        personal_info = applicant_resume.get("personal_info")
        if not personal_info:
            raise ValueError("personal_info is required")
        create_update_params : JobApplicant = {
            "name": str(personal_info.get("email")),
            "email_id":str(personal_info.get("email")),
            "applicant_name": str(personal_info.get("name")),
            "custom_pipeline_step": payload.get("pipeline_step_id"),
            "job_title": payload.get("job_opening_id"),
            "lower_range": 0.0,
            "upper_range": 0.0
        }
        job_applicant_doc = self.repo.job_applicant.create_or_update(create_update_params)
        if not job_applicant_doc:
            raise ValueError("cant create job_applicant_doc")
        applicant_resume_dto :ApplicantResumeDTO = {
            "job_applicant" : str(job_applicant_doc.get("name")),
            **applicant_resume
        }
        self.repo.applicant_resume.create_or_update(applicant_resume_dto)
        return job_applicant_doc


    def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]:
        return self.repo.job_applicant.job_applicant_bulk_update(payload)
