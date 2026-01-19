from typing import List
import frappe
from frappe import _
from mawhub.app.job.dto.job_applicant import JobApplicantBulkUpdateRequest, JobApplicantUpdateRequest
from mawhub.bootstrap import app_container

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def job_applicant_update(payload:JobApplicantUpdateRequest)->str:
    return app_container.job_usecase.job_applicant.job_applicant_update(payload)

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def job_applicant_bulk_update(payload:JobApplicantBulkUpdateRequest)->List[str]:
    return app_container.job_usecase.job_applicant.job_applicant_bulk_update(payload)
