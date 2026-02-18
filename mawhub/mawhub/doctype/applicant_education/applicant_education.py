# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
from typing import NotRequired, TypedDict
from frappe.model.document import Document

class ApplicantEducationDBModel(TypedDict):
    # frappe child table meta
    name: NotRequired[str]
    parent: NotRequired[str]
    parentfield: NotRequired[str]
    parenttype: NotRequired[str]
    idx: NotRequired[int]

    institution: NotRequired[str]
    degree: NotRequired[str]
    location: NotRequired[str]
    from_date: NotRequired[str]
    to_date: NotRequired[str]

class ApplicantEducation(Document):
	pass
