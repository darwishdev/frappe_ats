import json
from typing import List
from frappe import _
import frappe
from mawhub.app.job.dto.applicant_resume import  ApplicantResumeDTO
from mawhub.bootstrap import app_container
from werkzeug.wrappers import Response

from mawhub.pkg.pdfconvertor.pdfconvertor import extract_text_from_pdf  # <--- Correct Import

@frappe.whitelist(methods=["POST"])
def applicant_resume_parse(path: str):
    # Ensure this runs before the stream starts
    resume_text = ""
    try:
        resume_text = extract_text_from_pdf(path)
    except Exception as e:
        frappe.throw(f"Failed to read PDF: {str(e)}")

    def sse_generator():
        workflow = app_container.job_usecase.resume_agent
        try:
            # Iterate properly over the workflow
            yield f"data: Proccessing\n\n"
            if resume_text == "":
                raise frappe.ValidationError("cant parse the resume text")
            for update in workflow.run(resume_text , model_overrides={
                "labeler": "gemini-2.0-flash",
            }):
                yield f"data: {json.dumps(update)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"

    # PASS THE GENERATOR DIRECTLY HERE
    response = Response(sse_generator(), mimetype="text/event-stream")

    # Required headers for SSE
    response.headers.add("Cache-Control", "no-cache")
    response.headers.add("X-Accel-Filtering", "no") # Crucial for Nginx

    return response

@frappe.whitelist(methods=["POST"])
def applicant_resume_create_update(payload: ApplicantResumeDTO):
    return app_container.job_usecase.applicant_resume.applicant_resume_create_update(payload=payload)

@frappe.whitelist(methods=["POST"])

@frappe.whitelist(methods=["POST"])
def applicant_resume_bulk_create(payload: List[ApplicantResumeDTO]):
    return app_container.job_usecase.applicant_resume.applicant_resume_bulk_create(payload=payload)
