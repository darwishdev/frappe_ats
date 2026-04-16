# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

from typing import NotRequired, TypedDict
from frappe.model.document import Document


class WorkableEventDBModel(TypedDict):
    # frappe system fields
    name: NotRequired[str]          # workable event id (e.g. "438c02")
    idx: NotRequired[int]

    # core
    title: str
    event_type: NotRequired[str]    # "InterviewEvent"
    cancelled: NotRequired[int]     # Check

    # schedule
    starts_at: NotRequired[str]     # Datetime
    ends_at: NotRequired[str]       # Datetime

    # conference
    conference_type: NotRequired[str]
    conference_url: NotRequired[str]

    # relations
    job: NotRequired[str]           # Link → Workable Job (shortcode)
    job_title: NotRequired[str]
    candidate: NotRequired[str]     # Link → Workable Candidate (id)
    candidate_name: NotRequired[str]

    # text
    description: NotRequired[str]

    # JSON blob
    members: NotRequired[str]       # JSON-serialised list of member dicts


class WorkableEvent(Document):
    pass
