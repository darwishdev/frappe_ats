# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

from typing import NotRequired, TypedDict
from frappe.model.document import Document


class WorkableCandidateDBModel(TypedDict):
    # frappe system fields
    name: NotRequired[str]          # workable id (e.g. "8d53356")
    idx: NotRequired[int]

    # identity
    firstname: str
    lastname: NotRequired[str]
    email: NotRequired[str]
    phone: NotRequired[str]

    # profile
    headline: NotRequired[str]
    address: NotRequired[str]
    country: NotRequired[str]
    country_code: NotRequired[str]
    city: NotRequired[str]
    region: NotRequired[str]

    # pipeline status
    stage: NotRequired[str]                     # Link → Workable Stage (slug)
    stage_kind: NotRequired[str]                # fetched
    disqualified: NotRequired[int]              # Check
    disqualified_at: NotRequired[str | None]
    disqualification_reason: NotRequired[str]
    withdrew: NotRequired[int]                  # Check

    # outcome
    hired_at: NotRequired[str | None]
    moved_to_offer_at: NotRequired[str | None]
    sourced: NotRequired[int]                   # Check
    domain: NotRequired[str]
    outlet: NotRequired[str]
    common_source: NotRequired[str]
    common_source_category: NotRequired[str]

    # links
    profile_url: NotRequired[str]
    resume_url: NotRequired[str]
    resume_filename: NotRequired[str]
    linkedin_url: NotRequired[str]

    # text
    cover_letter: NotRequired[str]
    summary: NotRequired[str]

    # JSON blobs
    education_entries: NotRequired[str]         # Long Text — JSON serialised list
    experience_entries: NotRequired[str]        # Long Text — JSON serialised list
    skills: NotRequired[str]                    # Small Text — JSON serialised list

    # sync metadata
    workable_created_at: NotRequired[str]
    workable_updated_at: NotRequired[str]


class WorkableCandidate(Document):
    pass
