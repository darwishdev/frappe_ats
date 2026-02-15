import json
from typing import Iterator, List, cast
from frappe import _
import frappe
from mawhub.app.job.dto.applicant_resume_dto import  ApplicantResumeDTO
from mawhub.bootstrap import app_container
from werkzeug.wrappers import Response


@frappe.whitelist(methods=["POST","GET"])
def applicant_resume_parse(path: str,job_opening_id: str, pipeline_step_id: str):
    response = Response(
            app_container.job_usecase.applicant_resume.applicant_resume_parse(
                path,
                job_opening_id,
                pipeline_step_id,
                "123"

            ),
            mimetype="text/event-stream")
    response.headers.update({
        "Cache-Control": "no-cache",
        "X-Accel-Buffering": "no",  # Disables Nginx buffering for instant delivery
        "Connection": "keep-alive"
    })

    return response

@frappe.whitelist(methods=["POST", "GET"])
def applicant_resume_create_update(payload: ApplicantResumeDTO):
    return app_container.job_usecase.applicant_resume.applicant_resume_create_update(payload=payload)

@frappe.whitelist(methods=["POST", "GET"])

@frappe.whitelist(methods=["POST", "GET"])
def applicant_resume_bulk_create(payload: List[ApplicantResumeDTO]):
    return app_container.job_usecase.applicant_resume.applicant_resume_bulk_create(payload=payload)
