import frappe
from mawhub.app.job.repo.job_opening_repo import JobOpeningDBModel
from frappe import   Optional, _
import frappe
from mawhub.bootstrap import app_container
from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf



@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def job_opening_create_update(payload:JobOpeningDBModel):
    return app_container.job_usecase.job_opening.job_opening_create_update(payload)
@frappe.whitelist(methods=["GET"], allow_guest=True)
def job_opening_step_list(
        job_names:Optional[str],
):
    return  app_container.job_usecase.job_opening.job_opening_step_list(job_names)

@frappe.whitelist(methods=["PUT" , "POST"], allow_guest=True)
def job_opening_parse(file_path:str,document_text:str,request_id : str,user:str):
    if document_text == "":
        document_text = extract_text_from_pdf(file_path)
    parsed = app_container.job_usecase.job_opening.job_opening_parse(document_text,user,request_id)
    return parsed
