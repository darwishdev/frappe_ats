import frappe
from frappe import _

from mawhub.bootstrap import app_container
from mawhub.sqltypes.table_models import Interview

@frappe.whitelist(methods=["PUT","POST"], allow_guest=True)
def interview_create_update(payload:Interview)->Interview:
    return app_container.job_usecase.interview.interview_create_update(payload)
