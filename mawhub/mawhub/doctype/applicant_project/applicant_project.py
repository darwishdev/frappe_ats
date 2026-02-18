# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
from typing import NotRequired, TypedDict
from frappe.model.document import Document
class ApplicantProjectDBModel(TypedDict):
    # frappe child table meta
    name: NotRequired[str]
    parent: NotRequired[str]
    parentfield: NotRequired[str]
    parenttype: NotRequired[str]
    idx: NotRequired[int]

    title: str
    tech_stack: NotRequired[str]
    description: NotRequired[str]
    project_link: NotRequired[str]

class ApplicantProject(Document):
	pass
