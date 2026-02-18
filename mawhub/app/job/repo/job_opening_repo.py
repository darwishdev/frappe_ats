from typing import Literal, List, NotRequired, Protocol, TypedDict

from mawhub.mawhub.doctype.job_opening_applicant.job_opening_applicant import JobOpeningApplicantDBModel
from mawhub.mawhub.doctype.pipeline_step.pipeline_step import PipelineStepDBModel
from mawhub.pkg.baseclasses.app_repo import AppRepo, AppRepoInterface


class JobOpeningDBModel(TypedDict):
    # -------------------------
    # Frappe system fields
    # -------------------------
    name: NotRequired[str]
    # -------------------------
    # Core fields
    # -------------------------
    job_title: str
    designation: str
    company: str

    status: Literal["Open", "Closed"]

    posted_on: NotRequired[str]
    closes_on: NotRequired[str]
    closed_on: NotRequired[str]

    department: NotRequired[str]
    employment_type: NotRequired[str]
    location: NotRequired[str]

    description: NotRequired[str]

    staffing_plan: NotRequired[str]
    planned_vacancies: NotRequired[int]
    job_requisition: NotRequired[str]
    vacancies: NotRequired[int]
    publish: int
    route: NotRequired[str]
    publish_applications_received: int
    job_application_route: NotRequired[str]

    currency: NotRequired[str]
    lower_range: NotRequired[float]
    upper_range: NotRequired[float]
    salary_per: Literal["Month", "Year"]
    publish_salary_range: int

    # -------------------------
    # Template
    # -------------------------
    job_opening_template: NotRequired[str]

    # -------------------------
    # ✅ Custom scalar fields
    # -------------------------
    custom_pipeline: NotRequired[str]
    custom_parse_request_id: NotRequired[str]
    custom_customer: NotRequired[str]

    # -------------------------
    # ✅ Child tables
    # -------------------------
    custom_pipeline_steps: NotRequired[List[PipelineStepDBModel]]
    custom_applicants: NotRequired[List[JobOpeningApplicantDBModel]]

class JobOpeningRepoInterface(AppRepoInterface[JobOpeningDBModel],Protocol):
    ...


class JobOpeningRepo(AppRepo[JobOpeningDBModel]):
    def __init__(self):
        super().__init__(
            doc_name="Job Opening",
            name_key="name",
            scalar_fields=[
                "name",
                # core
                "job_title",
                "designation",
                "company",
                "status",

                "posted_on",
                "closes_on",
                "closed_on",

                "department",
                "employment_type",
                "location",
                "description",

                "staffing_plan",
                "planned_vacancies",
                "job_requisition",
                "vacancies",

                # publish / web
                "publish",
                "route",
                "publish_applications_received",
                "job_application_route",

                # salary
                "currency",
                "lower_range",
                "upper_range",
                "salary_per",
                "publish_salary_range",

                # template
                "job_opening_template",

                # custom scalars
                "custom_pipeline",
                "custom_parse_request_id",
                "custom_customer"
            ],
            child_tables={
                "custom_pipeline_steps" : "custom_pipeline_steps",
                "custom_applicants" : "custom_applicants",
            },
        )
