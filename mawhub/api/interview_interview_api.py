import json
import frappe
from google.auth import default
from mawhub.app.interview.repo.interview_interview_repo import InterviewDBModel, InterviewListFilter
from mawhub.bootstrap import app_container
import frappe


@frappe.whitelist(methods=["GET"], allow_guest=True)
def interview_list(
    status: str | None = None,
    job_applicant: str | None = None,
    job_opening: str | None = None,
    interview_round: str | None = None,
    scheduled_on_from: str | None = None,
    scheduled_on_to: str | None = None,
):
    filters: InterviewListFilter = {}
    if status is not None:
        filters["status"] = status
    if job_applicant is not None:
        filters["job_applicant"] = job_applicant
    if job_opening is not None:
        filters["job_opening"] = job_opening
    if interview_round is not None:
        filters["interview_round"] = interview_round
    if scheduled_on_from is not None:
        filters["scheduled_on_from"] = scheduled_on_from
    if scheduled_on_to is not None:
        filters["scheduled_on_to"] = scheduled_on_to
    return app_container.interview_usecase.interview.interview_list(filters)


@frappe.whitelist(methods=["GET"], allow_guest=True)
def interview_find(
        name:str,
):
    return  app_container.interview_usecase.interview.interview_find(name)

@frappe.whitelist(methods=["POST"])
def interview_create_update(
        payload:InterviewDBModel | str,
):
    if isinstance(payload,str):
        parsed_payload = json.loads(payload)
        return app_container.interview_usecase.interview.interview_create_update(parsed_payload)
    return  app_container.interview_usecase.interview.interview_create_update(payload)
