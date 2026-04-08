from typing import  List
from frappe import _
import frappe
from mawhub.app.applicant.dto.applicant_resume_dto import  ApplicantResumeDTO
from mawhub.bootstrap import app_container


@frappe.whitelist(methods=["POST","GET"])
def applicant_resume_parse(path: str,job_opening_id: str, pipeline_step_id: str):
    try:
        frappe.enqueue(
            method=applicant_resume_parse_bg,
            queue="long",
            timeout=800,
            is_async=True,
            now=False,
            enqueue_after_commit=False,
            at_front=True,
            path=path,
            job_opening_id=job_opening_id,
            pipeline_step_id=pipeline_step_id,
            user=frappe.session.user
        )

        return {
            "status": "queued",
            "message": "Document parsing started"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to enqueue job: {str(e)}"
        }
@frappe.whitelist(methods=["POST","GET"])
def applicant_resume_parse_bg(path: str,job_opening_id: str, pipeline_step_id: str,user:str):
    return app_container.applicant_usecase.applicant_resume.applicant_resume_parse(
                path,
                job_opening_id,
                user,
                pipeline_step_id
            )
@frappe.whitelist(methods=["POST", "GET"])
def applicant_resume_create_update(payload: ApplicantResumeDTO):
    return app_container.applicant_usecase.applicant_resume.applicant_resume_create_update(payload=payload)

@frappe.whitelist(methods=["POST", "GET"])

@frappe.whitelist(methods=["POST", "GET"])
def applicant_resume_bulk_create(payload: List[ApplicantResumeDTO]):
    return app_container.applicant_usecase.applicant_resume.applicant_resume_bulk_create(payload=payload)
