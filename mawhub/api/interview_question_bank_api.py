import frappe
from mawhub.bootstrap import app_container


@frappe.whitelist(methods=["POST"])
def personalize_question_bank(interview_id: str):
    return app_container.interview_usecase.question_bank.personalize_question_bank(interview_id)

