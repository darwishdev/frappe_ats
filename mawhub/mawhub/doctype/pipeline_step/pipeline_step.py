# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
from typing import TypedDict , Literal
from frappe.model.document import Document

class PipelineStepDBModel(TypedDict):
    name: str
    parent: str
    parentfield: str
    parenttype: str
    idx: int
    step_code: str
    step_name: str
    step_type: Literal[
        "screening",
        "interview",
        "assessment",
        "offer",
        "hired",
        "rejected",
    ]

class PipelineStep(Document):
	pass
