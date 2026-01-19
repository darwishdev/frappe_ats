from typing import List
import frappe
from frappe import _

from mawhub.app.job.dto.job_opening import JobOpeningDTO
from mawhub.bootstrap import app_container

@frappe.whitelist(methods=["GET","POST"], allow_guest=True)
def job_opening_list()->List[JobOpeningDTO]:
    return app_container.job_usecase.job_opening.job_opening_list("Administrator")


@frappe.whitelist(methods=["GET","POST"], allow_guest=True)
def job_opening_find(job:str)->JobOpeningDTO:
    return app_container.job_usecase.job_opening.job_opening_find(job)
