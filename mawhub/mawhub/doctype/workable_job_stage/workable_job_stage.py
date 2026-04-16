# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

from typing import NotRequired, TypedDict
from frappe.model.document import Document


class WorkableJobStageDBModel(TypedDict):
    # frappe system fields
    name: NotRequired[str]
    idx: NotRequired[int]

    # fields
    stage: str                      # Link → Workable Stage (slug)
    stage_name: NotRequired[str]    # fetched
    kind: NotRequired[str]          # fetched
    position: NotRequired[int]      # fetched


class WorkableJobStage(Document):
    pass
