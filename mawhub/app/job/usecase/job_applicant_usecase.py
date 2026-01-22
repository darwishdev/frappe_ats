from typing import List, Protocol

from frappe.model.document import Document
from mawhub.app.job.dto.applicant_resume import ApplicantResumeDTO
from mawhub.app.job.dto.job_applicant import JobApplicantBulkUpdateRequest, JobApplicantCreateWithResume
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.sqltypes.table_models import JobApplicant


class JobApplicantUsecaseInterface(Protocol):
	def job_applicant_create_update(self, payload: JobApplicant)->Document: ...
	def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]: ...

class JobApplicantUsecase:
    repo: JobRepoInterface
    def __init__(
        self,
        repo: JobRepoInterface,
    ):
        self.repo = repo

    def job_applicant_create_update(self, payload: JobApplicant)->Document:
        return self.repo.job_applicant.create_or_update(payload)



    def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]:
        return self.repo.job_applicant.job_applicant_bulk_update(payload)
