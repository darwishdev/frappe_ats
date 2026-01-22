from typing import List, Protocol

from frappe.model.document import Document
from mawhub.app.job.dto import applicant_resume
from mawhub.app.job.dto.job_applicant import JobApplicantBulkUpdateRequest, JobApplicantCreateWithResume
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.sqltypes.table_models import JobApplicant


class JobApplicantUsecaseInterface(Protocol):
	def job_applicant_create_update(self, payload: JobApplicant)->str: ...
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
    def job_applicant_create_with_resume(self, payload: JobApplicantCreateWithResume)->Document:
        applicant_resume = payload.get("applicant_resume")
        personal_info = applicant_resume.get("personal_info")
        if not personal_info:
            raise ValueError("personal_info is required")
        create_update_params : JobApplicant = {
            "name": str(personal_info.get("email")),
            "email_id":"a.dar@gma.cc",
            "applicant_name": "Ahmed Darwish",
            "idx": 1,
            "docstatus": 1,
            "lower_range": 3000.0,
            "upper_range": 5000.0
        }
        return self.repo.job_applicant.create_or_update(payload)


    def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]:
        return self.repo.job_applicant.job_applicant_bulk_update(payload)
