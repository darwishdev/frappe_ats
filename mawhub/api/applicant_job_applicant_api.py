import frappe
from frappe import  _
from frappe.model.document import Document
from mawhub.app.applicant.repo.job_applicant_repo import JobApplicantDBModel
from mawhub.bootstrap import app_container

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def job_applicant_create_update(payload:JobApplicantDBModel)->Document:
    return app_container.applicant_usecase.job_applicant.job_applicant_create_update(payload)

@frappe.whitelist(methods=["GET"] , allow_guest=True)
def job_applicant_find(name:str,job:str)->dict:
    return app_container.applicant_usecase.job_applicant.job_applicant_find(name,job)

