# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
from typing import NotRequired, TypedDict
from frappe.model.document import Document
class ApplicantExperienceDBModel(TypedDict):
    name: NotRequired[str]
    parent: NotRequired[str]
    parentfield: NotRequired[str]
    parenttype: NotRequired[str]
    idx: NotRequired[int]

    company: str
    role: NotRequired[str]
    duration: NotRequired[str]
    from_date: NotRequired[str]
    to_date: NotRequired[str]
    responsibilities: NotRequired[str]

class ApplicantExperience(Document):
	pass
