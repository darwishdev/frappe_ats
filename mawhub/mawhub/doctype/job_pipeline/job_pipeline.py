# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

# import frappe
from typing import List, NotRequired, TypedDict
from frappe.model.document import Document

from mawhub.mawhub.doctype.pipeline_step.pipeline_step import PipelineStepDBModel


class JobPipelineDBModel(TypedDict):
    # -------------------------
    # frappe system fields
    # -------------------------
    name: NotRequired[str]
    idx: NotRequired[int]

    # -------------------------
    # scalar fields
    # -------------------------
    description: NotRequired[str]
    is_primary: int

    # -------------------------
    # child tables
    # -------------------------
    steps: List[PipelineStepDBModel]
class JobPipeline(Document):
    @classmethod
    def get_list(cls, filters=None, fields=None, limit_start=0, limit_page_length=20, order_by=None, as_dict=False, debug=False):
        print("called here")
        return []
