# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

from typing import NotRequired, TypedDict
from frappe.model.document import Document


class WorkableJobCandidateDBModel(TypedDict):
    # frappe system fields
    name: NotRequired[str]
    idx: NotRequired[int]

    # fields
    candidate: str                          # Link → Workable Candidate (workable id)
    stage: NotRequired[str]                 # Link → Workable Stage (slug)
    stage_kind: NotRequired[str]            # fetched from stage
    disqualified: NotRequired[int]          # Check (0/1)
    hired_at: NotRequired[str | None]       # Datetime string


class WorkableJobCandidate(Document):
    pass
