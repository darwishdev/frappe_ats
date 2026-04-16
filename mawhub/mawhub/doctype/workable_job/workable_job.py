# Copyright (c) 2026, darwishdev and contributors
# For license information, please see license.txt

from typing import List, NotRequired, TypedDict
from frappe.model.document import Document

from mawhub.mawhub.doctype.workable_job_stage.workable_job_stage import WorkableJobStageDBModel
from mawhub.mawhub.doctype.workable_job_candidate.workable_job_candidate import WorkableJobCandidateDBModel


class WorkableJobDBModel(TypedDict):
    # frappe system fields
    name: NotRequired[str]              # shortcode — primary key (e.g. "EA389D5257")
    idx: NotRequired[int]

    # header
    workable_id: NotRequired[str]       # hex id (e.g. "1dd72a")
    title: str
    state: str                          # draft / published / archived / closed
    confidential: NotRequired[int]      # Check

    # job details
    full_title: NotRequired[str]
    code: NotRequired[str]
    department: NotRequired[str]
    workplace_type: NotRequired[str]    # on_site / remote / hybrid

    # classification
    employment_type: NotRequired[str]
    industry: NotRequired[str]
    job_function: NotRequired[str]
    experience: NotRequired[str]
    education: NotRequired[str]

    # location
    country: NotRequired[str]
    country_code: NotRequired[str]
    city: NotRequired[str]
    region: NotRequired[str]
    salary_currency: NotRequired[str]

    # urls
    url: NotRequired[str]
    application_url: NotRequired[str]
    shortlink: NotRequired[str]
    keywords: NotRequired[str]          # comma-separated string

    # rich text
    description: NotRequired[str]
    full_description: NotRequired[str]
    requirements: NotRequired[str]
    benefits: NotRequired[str]

    # child tables
    stages: NotRequired[List[WorkableJobStageDBModel]]
    candidates: NotRequired[List[WorkableJobCandidateDBModel]]

    # sync metadata
    workable_created_at: NotRequired[str]
    workable_updated_at: NotRequired[str]


class WorkableJob(Document):
    pass
