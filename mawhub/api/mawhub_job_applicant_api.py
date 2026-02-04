from typing import List
import frappe
from frappe import  _
from frappe.model.document import Document
from mawhub.app.job.dto.job_applicant import  JobApplicantBulkUpdateRequest, JobApplicantCreateWithResume
from mawhub.bootstrap import app_container
from typing import List

from mawhub.sqltypes.table_models import JobApplicant

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def job_applicant_bulk_update(payload:JobApplicantBulkUpdateRequest)->List[str]:
    return app_container.job_usecase.job_applicant.job_applicant_bulk_update(payload)

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def job_applicant_create_update(payload:JobApplicant)->Document:
    return app_container.job_usecase.job_applicant.job_applicant_create_update(payload)

@frappe.whitelist(methods=["GET"] , allow_guest=True)
def job_applicant_find(name:str)->dict:
    return app_container.job_usecase.job_applicant.job_applicant_find(name)

@frappe.whitelist(methods=["PUT","POST"])
def job_applicant_create_with_resume(payload:JobApplicantCreateWithResume)->Document:
    return app_container.job_usecase.applicant_resume.job_applicant_create_with_resume(payload)
