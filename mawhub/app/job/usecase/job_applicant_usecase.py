from typing import  List, Protocol

import frappe
from frappe.model.document import Document
from mawhub.app.job.repo.job_applicant_repo import JobApplicantDBModel
from mawhub.app.job.repo.job_repo import JobRepoInterface


class JobApplicantUsecaseInterface(Protocol):
    def job_applicant_create_update(self, payload: JobApplicantDBModel)->Document: ...
    def job_applicant_find(self, name: str, job: str)->dict: ...


class JobApplicantUsecase:
    repo: JobRepoInterface
    def __init__(
        self,
        repo: JobRepoInterface,
    ):
        self.repo = repo


    def job_applicant_create_update(self, payload: JobApplicantDBModel)->Document:
        return self.repo.job_applicant.create_or_update(payload)

    def job_applicant_find(self, name: str,job: str)->dict:
        return self.repo.job_applicant.job_applicant_find(name,job)


