import json
import frappe
from google.auth import default
from mawhub.app.interview.repo.interview_interview_repo import InterviewDBModel
from mawhub.bootstrap import app_container
import frappe



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
