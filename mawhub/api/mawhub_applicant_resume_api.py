import json
from typing import List
from frappe import _
import frappe
from mawhub.app.job.dto.applicant_resume import  ApplicantResumeDTO
from mawhub.bootstrap import app_container
from werkzeug.wrappers import Response

from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf  # <--- Correct Import

@frappe.whitelist(methods=["POST","GET"])
def applicant_resume_parse(path: str):
    # Ensure this runs before the stream starts
    resume_text = ""
    try:
        resume_text = extract_text_from_pdf(path)
    except Exception as e:
        frappe.throw(f"Failed to read PDF: {str(e)}")


    response = Response(app_container.job_usecase.applicant_resume.sse_generator(resume_text), mimetype="text/event-stream")

    # Required headers for SSE
    response.headers.add("Cache-Control", "no-cache")
    response.headers.add("X-Accel-Filtering", "no") # Crucial for Nginx

    return response

@frappe.whitelist(methods=["POST", "GET"])
def applicant_resume_create_update(payload: ApplicantResumeDTO):
    return app_container.job_usecase.applicant_resume.applicant_resume_create_update(payload=payload)

@frappe.whitelist(methods=["POST", "GET"])

@frappe.whitelist(methods=["POST", "GET"])
def applicant_resume_bulk_create(payload: List[ApplicantResumeDTO]):
    return app_container.job_usecase.applicant_resume.applicant_resume_bulk_create(payload=payload)
