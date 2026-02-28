import frappe
from mawhub.bootstrap import app_container
import frappe



@frappe.whitelist(methods=["GET"], allow_guest=True)
def interview_find(
        name:str,
):
    return  app_container.interview_usecase.interview.interview_find(name)
