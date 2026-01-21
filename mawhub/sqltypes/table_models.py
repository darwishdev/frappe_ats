# AUTO-GENERATED FILE
# Source: MariaDB information_schema
# Contains TypedDicts for $['tabJob Applicant', 'tabInterview', 'tabInterview Feedback']* tables
# Do not edit manually

from typing import TypedDict, NotRequired
from datetime import date, datetime

class JobApplicant(TypedDict):
    name: str
    creation: NotRequired[datetime]
    modified: NotRequired[datetime]
    modified_by: NotRequired[str]
    owner: NotRequired[str]
    docstatus: int
    idx: int
    applicant_name: NotRequired[str]
    email_id: NotRequired[str]
    phone_number: NotRequired[str]
    country: NotRequired[str]
    job_title: NotRequired[str]
    designation: NotRequired[str]
    status: NotRequired[str]
    source: NotRequired[str]
    source_name: NotRequired[str]
    employee_referral: NotRequired[str]
    applicant_rating: NotRequired[float]
    notes: NotRequired[str]
    cover_letter: NotRequired[str]
    resume_attachment: NotRequired[str]
    resume_link: NotRequired[str]
    currency: NotRequired[str]
    lower_range: float
    upper_range: float
    _user_tags: NotRequired[str]
    _comments: NotRequired[str]
    _assign: NotRequired[str]
    _liked_by: NotRequired[str]
    custom_pipeline_step: NotRequired[str]

class Interview(TypedDict):
    name: str
    creation: NotRequired[datetime]
    modified: NotRequired[datetime]
    modified_by: NotRequired[str]
    owner: NotRequired[str]
    docstatus: int
    idx: int
    interview_round: NotRequired[str]
    job_applicant: NotRequired[str]
    job_opening: NotRequired[str]
    designation: NotRequired[str]
    resume_link: NotRequired[str]
    status: NotRequired[str]
    scheduled_on: NotRequired[date]
    from_time: NotRequired[str]
    to_time: NotRequired[str]
    expected_average_rating: NotRequired[float]
    average_rating: NotRequired[float]
    interview_summary: NotRequired[str]
    reminded: int
    amended_from: NotRequired[str]
    _user_tags: NotRequired[str]
    _comments: NotRequired[str]
    _assign: NotRequired[str]
    _liked_by: NotRequired[str]

class InterviewFeedback(TypedDict):
    name: str
    creation: NotRequired[datetime]
    modified: NotRequired[datetime]
    modified_by: NotRequired[str]
    owner: NotRequired[str]
    docstatus: int
    idx: int
    interview: NotRequired[str]
    interview_round: NotRequired[str]
    job_applicant: NotRequired[str]
    interviewer: NotRequired[str]
    result: NotRequired[str]
    average_rating: NotRequired[float]
    feedback: NotRequired[str]
    amended_from: NotRequired[str]
    _user_tags: NotRequired[str]
    _comments: NotRequired[str]
    _assign: NotRequired[str]
    _liked_by: NotRequired[str]
