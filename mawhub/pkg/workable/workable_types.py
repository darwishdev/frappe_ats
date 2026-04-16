from typing import Any, Literal, NotRequired, TypedDict


# ---------------------------------------------------------------------------
# Shared / Primitive
# ---------------------------------------------------------------------------

class WorkableLocation(TypedDict):
    location_str: NotRequired[str]
    country: NotRequired[str]
    country_code: NotRequired[str]
    region: NotRequired[str | None]
    region_code: NotRequired[str | None]
    city: NotRequired[str | None]
    zip_code: NotRequired[str | None]
    telecommuting: NotRequired[bool]
    workplace_type: NotRequired[str]


class WorkableSalary(TypedDict):
    salary_currency: NotRequired[str]
    min_value: NotRequired[float | None]
    max_value: NotRequired[float | None]
    salary_per: NotRequired[str | None]


class WorkableDepartmentNode(TypedDict):
    id: int
    name: str


# ---------------------------------------------------------------------------
# Jobs
# ---------------------------------------------------------------------------

WorkableJobState = Literal["draft", "published", "archived", "closed"]


class WorkableJob(TypedDict):
    id: str
    title: str
    full_title: str
    shortcode: str
    code: str | None
    state: WorkableJobState
    sample: bool
    confidential: bool
    department: str | None
    department_hierarchy: list[WorkableDepartmentNode]
    url: str
    application_url: str
    shortlink: str
    workplace_type: str
    location: WorkableLocation
    locations: list[Any]
    salary: WorkableSalary
    created_at: str
    updated_at: str
    keywords: list[str] | None
    # detail-only (returned by GET /jobs/{shortcode})
    full_description: NotRequired[str | None]
    description: NotRequired[str | None]
    requirements: NotRequired[str | None]
    benefits: NotRequired[str | None]
    employment_type: NotRequired[str | None]
    industry: NotRequired[str | None]
    function: NotRequired[str | None]
    experience: NotRequired[str | None]
    education: NotRequired[str | None]


class WorkableJobsResponse(TypedDict):
    jobs: list[WorkableJob]
    paging: NotRequired[dict[str, str]]


# ---------------------------------------------------------------------------
# Stages
# ---------------------------------------------------------------------------

class WorkableStage(TypedDict):
    slug: str
    name: str
    kind: str
    position: int


class WorkableStagesResponse(TypedDict):
    stages: list[WorkableStage]


# ---------------------------------------------------------------------------
# Candidates
# ---------------------------------------------------------------------------

class WorkableResumeMetadata(TypedDict):
    filename: str | None
    filetype: str | None
    created_at: str
    updated_at: str


class WorkableSocialProfile(TypedDict):
    type: str
    name: str
    url: str


class WorkableEducationEntry(TypedDict):
    id: str
    degree: str | None
    school: str | None
    field_of_study: str | None
    start_date: str | None
    end_date: str | None


class WorkableExperienceEntry(TypedDict):
    id: str
    title: str | None
    summary: str | None
    start_date: str | None
    end_date: str | None
    company: str | None
    industry: str | None
    current: bool


class WorkableCandidate(TypedDict):
    id: str
    name: str
    firstname: str
    lastname: str
    headline: str | None
    account: dict[str, str]
    job: dict[str, str]
    stage: str
    stage_kind: str
    disqualified: bool
    disqualification_reason: str | None
    hired_at: str | None
    moved_to_offer_at: str | None
    sourced: bool
    profile_url: str
    address: str | None
    phone: str | None
    email: str | None
    domain: str | None
    outlet: str | None
    common_source: str | None
    common_source_category: str | None
    created_at: str
    updated_at: str
    resume_metadata: NotRequired[WorkableResumeMetadata | None]
    # detail-only
    image_url: NotRequired[str | None]
    cover_letter: NotRequired[str | None]
    summary: NotRequired[str | None]
    education_entries: NotRequired[list[WorkableEducationEntry]]
    experience_entries: NotRequired[list[WorkableExperienceEntry]]
    skills: NotRequired[list[Any]]
    answers: NotRequired[list[Any]]
    resume_url: NotRequired[str | None]
    social_profiles: NotRequired[list[WorkableSocialProfile]]
    disqualified_at: NotRequired[str | None]
    withdrew: NotRequired[bool]


class WorkableCandidatesResponse(TypedDict):
    candidates: list[WorkableCandidate]
    paging: NotRequired[dict[str, str]]


# ---------------------------------------------------------------------------
# Activities
# ---------------------------------------------------------------------------

class WorkableActivity(TypedDict):
    id: str
    action: str
    stage_name: str | None
    action_stage: dict[str, Any] | None
    target_stage: dict[str, Any] | None
    created_at: str
    updated_at: str
    member: NotRequired[dict[str, str] | None]
    body: NotRequired[str | None]


class WorkableActivitiesResponse(TypedDict):
    activities: list[WorkableActivity]


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

class WorkableEventMember(TypedDict):
    id: str
    name: str
    type: str
    status: str


class WorkableConference(TypedDict):
    type: str | None
    url: str | None


class WorkableEvent(TypedDict):
    id: str
    title: str
    description: str | None
    type: str                               # e.g. "InterviewEvent"
    starts_at: str
    ends_at: str
    cancelled: bool
    job: dict[str, str]                     # {shortcode, title}
    candidate: dict[str, str]               # {id, name}
    members: list[WorkableEventMember]
    conference: WorkableConference | None


class WorkableEventsResponse(TypedDict):
    events: list[WorkableEvent]
    paging: NotRequired[dict[str, str]]


# ---------------------------------------------------------------------------
# Subscriptions (webhooks)
# ---------------------------------------------------------------------------

WorkableEventType = Literal[
    "candidate_created",
    "candidate_updated",
    "candidate_moved",
    "candidate_hired",
    "job_published",
    "job_closed",
    "job_archived",
]


class WorkableSubscription(TypedDict):
    id: int
    event: str
    target: str
    valid_until: str | None
    created_at: str
    stage_slug: str | None
    job_shortcode: str | None


class WorkableSubscriptionsResponse(TypedDict):
    subscriptions: list[WorkableSubscription]
