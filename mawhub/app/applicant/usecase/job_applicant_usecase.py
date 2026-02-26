from typing import Protocol

from frappe.model.document import Document
from mawhub.app.applicant.repo.applicant_repo import ApplicantRepoInterface
from mawhub.app.job.repo.job_applicant_repo import JobApplicantDBModel


class JobApplicantUsecaseInterface(Protocol):
    def job_applicant_create_update(self, payload: JobApplicantDBModel)->Document: ...
    def job_applicant_find(self, name: str, job: str)->dict: ...


class JobApplicantUsecase:
    repo: ApplicantRepoInterface
    def __init__(
        self,
        repo: ApplicantRepoInterface,
    ):
        self.repo = repo


    def job_applicant_create_update(self, payload: JobApplicantDBModel)->Document:
        return self.repo.job_applicant.create_or_update(payload)

    def job_applicant_find(self, name: str,job: str)->dict:
        return self.repo.job_applicant.job_applicant_find(name,job)


