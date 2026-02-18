# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
from typing import TypedDict
from frappe.model.document import Document
class JobOpeningApplicantDBModel(TypedDict):
    name: str
    parent: str
    parentfield: str
    parenttype: str
    idx: int

    step_code: str
    job_applicant: str
    applicant_resume: str
    comment: str | None

    invalidated_at: str | None
    invalidated_by: str | None

class JobOpeningApplicant(Document):
	pass
