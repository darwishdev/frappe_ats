# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

from typing import NotRequired, TypedDict
from frappe.model.document import Document


class WorkableStageDBModel(TypedDict):
    # frappe system fields
    name: NotRequired[str]          # slug — primary key (e.g. "interview")
    idx: NotRequired[int]

    # scalar fields
    stage_name: str                 # display name
    kind: str                       # sourced / applied / phone-screen / assessment / interview / offer / hired
    position: NotRequired[int]


class WorkableStage(Document):
    pass
