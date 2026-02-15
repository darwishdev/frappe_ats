from typing import Dict, List, Protocol, cast

import frappe
from frappe.model.document import Document
from mawhub.app.job.dto.job_applicant_dto import JobApplicantBulkUpdateRequest
from mawhub.app.job.repo.job_repo import JobRepoInterface
from mawhub.sqltypes.table_models import JobApplicant


class JobApplicantUsecaseInterface(Protocol):
    def job_applicant_create_update(self, payload: JobApplicant)->Document: ...
    def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]: ...
    def job_applicant_find(self, name: str, job: str)->dict: ...


class JobApplicantUsecase:
    repo: JobRepoInterface
    def __init__(
        self,
        repo: JobRepoInterface,
    ):
        self.repo = repo

    def job_applicant_create_update(self, payload: JobApplicant)->Document:
        step = payload.get("custom_pipeline_step")
        if not step:
            step_names = frappe.db.sql("""
                SELECT name FROM `tabPipeline Step` s
                WHERE s.parent = %s
                ORDER BY idx ASC
                LIMIT 1
                                 """ , (payload.get('job_title'),),pluck=True ) or []
            typed_names = cast(List[str] , step_names)
            if len(typed_names) == 0:
                raise frappe.ValidationError("Please set valid pipeline steps to the job opening")
            payload["custom_pipeline_step"] = typed_names[0]
        return self.repo.job_applicant.create_or_update(payload)

    def job_applicant_find(self, name: str,job: str)->dict:
        return self.repo.job_applicant.job_applicant_find(name,job)


    def job_applicant_bulk_update(self, payload: JobApplicantBulkUpdateRequest)->List[str]:
        return self.repo.job_applicant.job_applicant_bulk_update(payload)
