# AUTO-GENERATED FILE
# Source: MariaDB information_schema
# Contains TypedDicts for $['tabInterview', 'tabInterview Feedback']* tables
# Do not edit manually

from typing import TypedDict, NotRequired
from datetime import date, datetime

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

